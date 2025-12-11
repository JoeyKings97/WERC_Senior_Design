import asyncio
import os
from typing import Any, AsyncGenerator, Dict

import aiosqlite
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from .config import Settings


class DataStore:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.sqlite_conn: aiosqlite.Connection | None = None
        self.influx_client: InfluxDBClient | None = None
        self.influx_write_api = None
        self.influx_query_api = None
        self.live_queue: asyncio.Queue = asyncio.Queue(maxsize=100)

    async def connect(self):
        if self.settings.datastore_backend == "sqlite":
            # Ensure parent directory exists for SQLite file
            db_path = self.settings.sqlite_path
            parent = os.path.dirname(db_path)
            if parent and not os.path.exists(parent):
                os.makedirs(parent, exist_ok=True)
            self.sqlite_conn = await aiosqlite.connect(db_path)
            await self.sqlite_conn.execute(
                """
                CREATE TABLE IF NOT EXISTS telemetry (
                    ts INTEGER PRIMARY KEY,
                    humidity REAL,
                    temperature REAL,
                    airflow REAL,
                    condensate_rate REAL,
                    pump_status INTEGER
                )
                """
            )
            await self.sqlite_conn.commit()
        elif self.settings.datastore_backend == "influx":
            if not all([
                self.settings.influx_url,
                self.settings.influx_token,
                self.settings.influx_org,
                self.settings.influx_bucket,
            ]):
                raise ValueError("InfluxDB config missing: set INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET")
            self.influx_client = InfluxDBClient(
                url=self.settings.influx_url,
                token=self.settings.influx_token,
                org=self.settings.influx_org,
            )
            self.influx_write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
            self.influx_query_api = self.influx_client.query_api()
        # Mongo stub still pending

    async def close(self):
        if self.sqlite_conn:
            await self.sqlite_conn.close()
        if self.influx_client:
            self.influx_client.close()

    async def write_measurement(self, payload: Dict[str, Any]):
        payload = payload.copy()
        payload.setdefault("ts", int(asyncio.get_event_loop().time() * 1000))
        await self.live_queue.put(payload)
        if self.settings.datastore_backend == "sqlite" and self.sqlite_conn:
            await self.sqlite_conn.execute(
                "INSERT INTO telemetry (ts, humidity, temperature, airflow, condensate_rate, pump_status) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    payload.get("ts"),
                    payload.get("humidity"),
                    payload.get("temperature"),
                    payload.get("airflow"),
                    payload.get("condensate_rate"),
                    payload.get("pump_status"),
                ),
            )
            await self.sqlite_conn.commit()
        elif self.settings.datastore_backend == "influx" and self.influx_write_api:
            await asyncio.to_thread(self._write_influx, payload)

    async def latest_metrics(self) -> Dict[str, Any]:
        if self.settings.datastore_backend == "sqlite" and self.sqlite_conn:
            cursor = await self.sqlite_conn.execute(
                "SELECT ts, humidity, temperature, airflow, condensate_rate, pump_status FROM telemetry ORDER BY ts DESC LIMIT 1"
            )
            row = await cursor.fetchone()
            if row:
                return {
                    "ts": row[0],
                    "humidity": row[1],
                    "temperature": row[2],
                    "airflow": row[3],
                    "condensate_rate": row[4],
                    "pump_status": row[5],
                }
        elif self.settings.datastore_backend == "influx" and self.influx_query_api:
            return await asyncio.to_thread(self._latest_influx)
        return {}

    async def stream_live(self) -> AsyncGenerator[Dict[str, Any], None]:
        while True:
            sample = await self.live_queue.get()
            yield sample

    def _write_influx(self, payload: Dict[str, Any]):
        point = (
            Point("telemetry")
            .time(payload.get("ts"), WritePrecision.MS)
            .field("humidity", payload.get("humidity"))
            .field("temperature", payload.get("temperature"))
            .field("airflow", payload.get("airflow"))
            .field("condensate_rate", payload.get("condensate_rate"))
            .field("pump_status", payload.get("pump_status"))
        )
        self.influx_write_api.write(bucket=self.settings.influx_bucket, org=self.settings.influx_org, record=point)

    def _latest_influx(self) -> Dict[str, Any]:
        query = f"""
        from(bucket: "{self.settings.influx_bucket}")
          |> range(start: -24h)
          |> filter(fn: (r) => r["_measurement"] == "telemetry")
          |> last()
        """
        tables = self.influx_query_api.query(query=query, org=self.settings.influx_org)
        latest: Dict[str, Any] = {}
        for table in tables:
            for record in table.records:
                field = record.get_field()
                latest[field] = record.get_value()
                ts = int(record.get_time().timestamp() * 1000)
                latest["ts"] = ts
        return latest
