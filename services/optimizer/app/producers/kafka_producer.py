import json
import logging
import time

from kafka import KafkaAdminClient, KafkaProducer
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError

from app.core.config import settings

logger = logging.getLogger(__name__)


class KafkaScheduleProducer:
    TOPICS = (settings.KAFKA_SCHEDULE_TOPIC,)

    def __init__(self):
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        self._producer: KafkaProducer | None = None
        self._admin: KafkaAdminClient | None = None
        self._topics_ready = False

    def _connect(self, retries: int = 5, delay: int = 2):
        if self._producer is not None and self._admin is not None:
            return

        last_error = None
        for attempt in range(1, retries + 1):
            try:
                logger.info("Connecting optimizer producer to Kafka (%s/%s)", attempt, retries)
                self._producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda value: json.dumps(value, default=str).encode("utf-8"),
                    key_serializer=lambda value: str(value).encode("utf-8") if value is not None else None,
                    retries=5,
                    linger_ms=10,
                    acks="all",
                )
                self._admin = KafkaAdminClient(
                    bootstrap_servers=self.bootstrap_servers,
                    client_id="ecs-optimizer-admin",
                )
                return
            except Exception as exc:
                last_error = exc
                logger.warning("Kafka producer connection failed: %s", exc)
                time.sleep(delay)

        raise RuntimeError(
            f"Could not connect optimizer producer to Kafka after {retries} attempts: {last_error}"
        )

    def _ensure_topics(self):
        if self._topics_ready:
            return

        self._connect()

        for topic_name in self.TOPICS:
            try:
                self._admin.create_topics(
                    [
                        NewTopic(
                            name=topic_name,
                            num_partitions=1,
                            replication_factor=1,
                        )
                    ]
                )
                logger.info("Created topic: %s", topic_name)
            except TopicAlreadyExistsError:
                logger.info("Topic already exists: %s", topic_name)
            except Exception as exc:
                logger.warning("Topic setup issue for %s: %s", topic_name, exc)

        self._topics_ready = True

    def send(self, topic: str, message: dict, key: str | None = None):
        self._ensure_topics()

        if self._producer is None:
            raise RuntimeError("Kafka producer is not initialized.")

        future = self._producer.send(topic, value=message, key=key)

        try:
            metadata = future.get(timeout=10)
            self._producer.flush()
            return {
                "topic": metadata.topic,
                "partition": metadata.partition,
                "offset": metadata.offset,
            }
        except Exception:
            logger.exception("Failed to publish optimizer schedule to Kafka")
            raise

    def healthcheck(self) -> bool:
        try:
            self._connect(retries=1, delay=0)
            if self._admin is None or self._producer is None:
                return False
            self._admin.list_topics()
            return True
        except Exception:
            logger.exception("Optimizer Kafka healthcheck failed")
            return False

    def close(self):
        if self._producer is not None:
            self._producer.flush()
            self._producer.close()
        if self._admin is not None:
            self._admin.close()


kafka_producer = KafkaScheduleProducer()
