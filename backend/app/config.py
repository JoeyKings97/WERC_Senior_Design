from functools import lru_cache
from pydantic import BaseModel, Field
import os


class Settings(BaseModel):
    env: str = Field(default=os.getenv("APP_ENV", "dev"))
    modbus_host: str = Field(default=os.getenv("MODBUS_HOST", "127.0.0.1"))
    modbus_port: int = Field(default=int(os.getenv("MODBUS_PORT", "5020")))
    modbus_unit_id: int = Field(default=int(os.getenv("MODBUS_UNIT_ID", "1")))
    poll_interval_seconds: float = Field(default=float(os.getenv("POLL_INTERVAL_SECONDS", "2.0")))
    datastore_backend: str = Field(default=os.getenv("DATASTORE_BACKEND", "sqlite"))  # sqlite|influx|mongo
    sqlite_path: str = Field(default=os.getenv("SQLITE_PATH", "./data/telemetry.db"))
    influx_url: str = Field(default=os.getenv("INFLUX_URL", ""))
    influx_token: str = Field(default=os.getenv("INFLUX_TOKEN", ""))
    influx_org: str = Field(default=os.getenv("INFLUX_ORG", ""))
    influx_bucket: str = Field(default=os.getenv("INFLUX_BUCKET", ""))
    mongo_url: str = Field(default=os.getenv("MONGO_URL", ""))
    mongo_db: str = Field(default=os.getenv("MONGO_DB", "coolingtower"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
