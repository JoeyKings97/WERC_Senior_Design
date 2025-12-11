import asyncio
from pymodbus.client import AsyncModbusTcpClient
from .config import Settings


class ModbusClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client: AsyncModbusTcpClient | None = None

    async def connect(self):
        self.client = AsyncModbusTcpClient(self.settings.modbus_host, port=self.settings.modbus_port)
        await self.client.connect()

    async def close(self):
        if self.client:
            await self.client.close()

    async def read_registers(self, address: int, count: int = 4):
        if not self.client:
            await self.connect()
        result = await self.client.read_input_registers(address=address, count=count, unit=self.settings.modbus_unit_id)
        return result.registers if result.isError() is False else []

    async def write_coil(self, address: int, value: bool):
        if not self.client:
            await self.connect()
        await self.client.write_coil(address=address, value=value, unit=self.settings.modbus_unit_id)

    async def poll_snapshot(self) -> dict:
        # Example mapping: adjust addresses to match PLC tag map
        registers = await self.read_registers(address=0, count=4)
        if not registers:
            return {}
        humidity, temperature, airflow, condensate = registers
        return {
            "humidity": humidity / 10,
            "temperature": temperature / 10,
            "airflow": airflow / 10,
            "condensate_rate": condensate / 10,
        }
