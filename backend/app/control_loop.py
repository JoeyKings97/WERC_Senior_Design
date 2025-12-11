import asyncio
from .config import Settings
from .modbus_client import ModbusClient
from .data_store import DataStore


class ControlLoop:
    def __init__(self, settings: Settings, modbus: ModbusClient, store: DataStore):
        self.settings = settings
        self.modbus = modbus
        self.store = store
        self._task: asyncio.Task | None = None
        self._enabled = False

    def start(self):
        if not self._task:
            self._task = asyncio.create_task(self._run())

    def stop(self):
        if self._task:
            self._task.cancel()
            self._task = None

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    async def _run(self):
        while True:
            await asyncio.sleep(self.settings.poll_interval_seconds)
            snapshot = await self.modbus.poll_snapshot()
            if snapshot:
                snapshot["pump_status"] = 1 if self._enabled else 0
                await self.store.write_measurement(snapshot)
                if self._enabled:
                    await self._apply_control(snapshot)

    async def _apply_control(self, snapshot: dict):
        # Simple rule: enable pump if condensate rate below target
        target_rate = 5.0
        should_run = snapshot.get("condensate_rate", 0) < target_rate
        await self.modbus.write_coil(address=1, value=should_run)
