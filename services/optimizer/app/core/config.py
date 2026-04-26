import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://ecs_user:ecs_password@localhost:5432/ecs_db",
    )

    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS",
        "localhost:9092",
    )
    KAFKA_CONSUMER_GROUP: str = os.getenv(
        "KAFKA_CONSUMER_GROUP",
        "ecs-optimizer-consumer",
    )
    KAFKA_SCHEDULE_TOPIC: str = os.getenv(
        "KAFKA_SCHEDULE_TOPIC",
        "ecs_schedule",
    )
    DEFAULT_GAS_COST: float = float(os.getenv("DEFAULT_GAS_COST", "0"))
    DEFAULT_INITIAL_BATTERY_SOC: float = float(
        os.getenv("DEFAULT_INITIAL_BATTERY_SOC", "0")
    )


settings = Settings()
