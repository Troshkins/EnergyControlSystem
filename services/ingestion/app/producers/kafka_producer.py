import json
import time
import logging
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

from app.core.config import settings

logger = logging.getLogger(__name__)


class KafkaEventProducer:
    def __init__(self):
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        self.producer = None

        self._connect()
        self._ensure_topics()

    def _connect(self, retries=10, delay=5):
        for attempt in range(retries):
            try:
                logger.info(f"Connecting to Kafka ({attempt+1}/{retries})...")

                self.producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
                    key_serializer=lambda v: str(v).encode("utf-8") if v else None,
                    retries=5,
                    linger_ms=10,
                )

                logger.info("Connected to Kafka")
                return

            except Exception as e:
                logger.warning(f"Kafka connection failed: {e}")
                time.sleep(delay)

        raise RuntimeError("Could not connect to Kafka after retries")

    def _ensure_topics(self):
        try:
            admin = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)

            topics = [
                NewTopic(name="price_signals", num_partitions=1, replication_factor=1),
                NewTopic(name="demand_forecasts", num_partitions=1, replication_factor=1),
                NewTopic(name="intraday_updates", num_partitions=1, replication_factor=1),
            ]

            for topic in topics:
                try:
                    admin.create_topics([topic])
                    logger.info(f"Created topic: {topic.name}")
                except TopicAlreadyExistsError:
                    logger.info(f"Topic already exists: {topic.name}")
                except Exception as e:
                    logger.warning(f"Topic creation issue: {e}")

        except Exception as e:
            logger.warning(f"Kafka admin unavailable: {e}")

    def send(self, topic: str, message: dict, key: str | None = None):
        if not self.producer:
            raise RuntimeError("Kafka producer not initialized")

        try:
            future = self.producer.send(topic, value=message, key=key)
            record_metadata = future.get(timeout=10)

            logger.info(
                f"Sent to {record_metadata.topic} "
                f"(partition={record_metadata.partition}, offset={record_metadata.offset})"
            )

            return {
                "topic": record_metadata.topic,
                "partition": record_metadata.partition,
                "offset": record_metadata.offset,
            }

        except Exception as e:
            logger.error(f"Kafka send failed: {e}")
            raise e

    def close(self):
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("Kafka producer closed")


kafka_producer = KafkaEventProducer()
