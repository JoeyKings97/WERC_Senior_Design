import asyncio
import random
import httpx

BACKEND_URL = "http://127.0.0.1:8000/ingest"


async def push_loop():
    async with httpx.AsyncClient() as client:
        while True:
            payload = {
                "humidity": round(random.uniform(40, 80), 1),
                "temperature": round(random.uniform(15, 45), 1),
                "airflow": round(random.uniform(5, 20), 1),
                "condensate_rate": round(random.uniform(0, 10), 1),
                "pump_status": random.choice([0, 1]),
            }
            await client.post(BACKEND_URL, json=payload)
            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(push_loop())
