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
    KAFKA_INTRADAY_TOPIC: str = os.getenv(
        "KAFKA_INTRADAY_TOPIC",
        "intraday_actions",
    )
    DEFAULT_GAS_COST: float = float(os.getenv("DEFAULT_GAS_COST", "0"))
    HIGH_INTRADAY_PRICE_THRESHOLD: float = float(
        os.getenv("HIGH_INTRADAY_PRICE_THRESHOLD", "200")
    )


settings = Settings()
