from fastapi import FastAPI, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from .config import Settings, get_settings
from .modbus_client import ModbusClient
from .data_store import DataStore
from .control_loop import ControlLoop

app = FastAPI(title="Cooling Tower Water Recovery", version="0.1.0")

# Allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = Settings()
modbus_client = ModbusClient(settings)
data_store = DataStore(settings)
control_loop = ControlLoop(settings, modbus_client, data_store)


@app.on_event("startup")
async def on_startup():
    await data_store.connect()
    control_loop.start()


@app.on_event("shutdown")
async def on_shutdown():
    control_loop.stop()
    await data_store.close()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/config")
async def config(settings: Settings = Depends(get_settings)):
    return settings.model_dump()


@app.get("/metrics")
async def metrics():
    # Placeholder for KPIs (recovery rate, pump status, humidity, temp)
    return await data_store.latest_metrics()


@app.post("/ingest")
async def ingest(payload: dict):
    # Accept sensor readings when pushing (MQTT/webhook), fallback to PLC polling otherwise
    await data_store.write_measurement(payload)
    return {"stored": True}


@app.websocket("/ws/telemetry")
async def telemetry_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        async for sample in data_store.stream_live():
            await websocket.send_json(sample)
    except Exception:
        await websocket.close()


@app.post("/control/enable")
async def enable_control():
    control_loop.enable()
    return {"control_enabled": True}


@app.post("/control/disable")
async def disable_control():
    control_loop.disable()
    return {"control_enabled": False}
