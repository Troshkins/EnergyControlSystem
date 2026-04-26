import json
import logging
from collections import defaultdict
from datetime import datetime
from uuid import uuid4

from kafka import KafkaConsumer

from app.core.config import settings
from app.core.database import SessionLocal
from app.producers.kafka_producer import kafka_producer
from app.repositories.schedule_repo import get_latest_asset_constraints, save_day_ahead_schedule
from app.schemas.optimization import (
    DayAheadOptimizationRequest,
    DemandPoint,
    PricePoint,
)
from app.services.day_ahead_optimizer import optimize_day_ahead

logger = logging.getLogger(__name__)


class OptimizerKafkaConsumer:
    PRICE_TOPIC = "price_signals"
    DEMAND_TOPIC = "demand_forecasts"

    def __init__(self):
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        self.group_id = settings.KAFKA_CONSUMER_GROUP
        self.schedule_topic = settings.KAFKA_SCHEDULE_TOPIC
        self._buffers: dict[str, dict[str, list[dict]]] = defaultdict(
            lambda: {"prices": [], "demand_forecast": []}
        )

    def create_consumer(self) -> KafkaConsumer:
        return KafkaConsumer(
            self.PRICE_TOPIC,
            self.DEMAND_TOPIC,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda value: json.loads(value.decode("utf-8")),
            auto_offset_reset="latest",
            enable_auto_commit=True,
        )

    def run_forever(self):
        consumer = self.create_consumer()
        logger.info(
            "Optimizer Kafka consumer started for topics %s, %s",
            self.PRICE_TOPIC,
            self.DEMAND_TOPIC,
        )

        try:
            for message in consumer:
                self.process_message(message.topic, message.value)
        finally:
            consumer.close()

    def process_message(self, topic: str, payload: dict):
        points = self._extract_points(topic, payload)
        if not points:
            logger.warning("Skipping Kafka message with no usable points from topic=%s", topic)
            return

        affected_dates = set()
        for point in points:
            timestamp = self._parse_timestamp(point["timestamp"])
            schedule_date = timestamp.date().isoformat()
            affected_dates.add(schedule_date)
            key = "prices" if topic == self.PRICE_TOPIC else "demand_forecast"
            normalized_point = {
                "timestamp": timestamp.isoformat(),
                "price": point.get("price"),
                "demand": point.get("demand"),
            }

            existing_points = self._buffers[schedule_date][key]
            existing_points = [
                item for item in existing_points if item["timestamp"] != normalized_point["timestamp"]
            ]
            existing_points.append(normalized_point)
            self._buffers[schedule_date][key] = existing_points

        for schedule_date in affected_dates:
            self._try_optimize_for_date(schedule_date)

    def _extract_points(self, topic: str, payload: dict) -> list[dict]:
        if not isinstance(payload, dict):
            return []

        if topic == self.PRICE_TOPIC:
            if isinstance(payload.get("prices"), list):
                return payload["prices"]
            if "timestamp" in payload and "price" in payload:
                return [payload]

        if topic == self.DEMAND_TOPIC:
            if isinstance(payload.get("demand_forecast"), list):
                return payload["demand_forecast"]
            if isinstance(payload.get("forecasts"), list):
                return payload["forecasts"]
            if "timestamp" in payload and "demand" in payload:
                return [payload]

        return []

    def _try_optimize_for_date(self, schedule_date: str):
        buffered = self._buffers[schedule_date]
        if len(buffered["prices"]) < 24 or len(buffered["demand_forecast"]) < 24:
            return

        db = SessionLocal()
        try:
            asset_constraints = get_latest_asset_constraints(db)
            if asset_constraints is None:
                logger.warning(
                    "Skipping Kafka-triggered optimization for %s because asset constraints are missing",
                    schedule_date,
                )
                return

            request = DayAheadOptimizationRequest(
                prices=[
                    PricePoint(
                        timestamp=self._parse_timestamp(point["timestamp"]),
                        price=float(point["price"]),
                    )
                    for point in buffered["prices"]
                ],
                demand_forecast=[
                    DemandPoint(
                        timestamp=self._parse_timestamp(point["timestamp"]),
                        demand=float(point["demand"]),
                    )
                    for point in buffered["demand_forecast"]
                ],
                asset_constraints=asset_constraints,
            )

            optimization_response = optimize_day_ahead(request)
            run_id = uuid4()
            optimization_response.run_id = run_id
            save_day_ahead_schedule(db, run_id, optimization_response)
            kafka_producer.send(
                self.schedule_topic,
                optimization_response.model_dump(mode="json"),
                key=str(run_id),
            )
            logger.info("Published optimized schedule for %s with run_id=%s", schedule_date, run_id)
            del self._buffers[schedule_date]
        except Exception:
            logger.exception("Kafka-triggered optimization failed for %s", schedule_date)
        finally:
            db.close()

    @staticmethod
    def _parse_timestamp(value: str) -> datetime:
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)


def run_consumer():
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    consumer = OptimizerKafkaConsumer()
    consumer.run_forever()


if __name__ == "__main__":
    run_consumer()
