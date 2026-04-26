import json
import logging
from datetime import datetime

from kafka import KafkaConsumer

from app.core.config import settings
from app.core.database import SessionLocal
from app.schemas.intraday import IntradayOptimizationRequest
from app.services.intraday_optimizer import optimize_intraday_update

logger = logging.getLogger(__name__)


class KafkaConsumerClient:
    TOPIC = "intraday_updates"

    def __init__(self):
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS

    def create_consumer(self) -> KafkaConsumer:
        return KafkaConsumer(
            self.TOPIC,
            bootstrap_servers=self.bootstrap_servers,
            group_id="ecs-intraday-consumer",
            value_deserializer=lambda value: json.loads(value.decode("utf-8")),
            auto_offset_reset="latest",
            enable_auto_commit=True,
        )

    def run_forever(self):
        consumer = self.create_consumer()
        logger.info("Intraday Kafka consumer started for topic %s", self.TOPIC)

        try:
            for message in consumer:
                self.process_message(message.value)
        finally:
            consumer.close()

    def process_message(self, payload: dict):
        requests = self._extract_requests(payload)
        if not requests:
            logger.warning("Skipping intraday update message with no usable payload")
            return

        for request in requests:
            db = SessionLocal()
            try:
                optimize_intraday_update(request, db)
            except Exception:
                logger.exception(
                    "Failed to process intraday Kafka update for timestamp=%s",
                    request.timestamp.isoformat(),
                )
            finally:
                db.close()

    def _extract_requests(
        self,
        payload: dict,
    ) -> list[IntradayOptimizationRequest]:
        if not isinstance(payload, dict):
            return []

        if isinstance(payload.get("updates"), list):
            return [self._build_request(item) for item in payload["updates"] if isinstance(item, dict)]

        if "timestamp" in payload and "actual_demand" in payload:
            return [self._build_request(payload)]

        return []

    @staticmethod
    def _build_request(payload: dict) -> IntradayOptimizationRequest:
        timestamp = payload["timestamp"]
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        return IntradayOptimizationRequest(
            timestamp=timestamp,
            actual_demand=float(payload["actual_demand"]),
            intraday_price=(
                float(payload["intraday_price"])
                if payload.get("intraday_price") is not None
                else None
            ),
            run_id=payload.get("run_id"),
            current_battery_soc=(
                float(payload["current_battery_soc"])
                if payload.get("current_battery_soc") is not None
                else None
            ),
        )


def run_consumer():
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    kafka_consumer = KafkaConsumerClient()
    kafka_consumer.run_forever()


if __name__ == "__main__":
    run_consumer()
