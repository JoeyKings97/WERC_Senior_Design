# Cooling Tower Water Recovery Control/Monitoring

Stack: Python FastAPI backend (Modbus + data logging), React/Vite dashboard, SQLite default with optional Influx/Mongo, PLC integration via Modbus. Simulated telemetry included.

## Quick start (Windows PowerShell)

```powershell
# Backend
./scripts/run-backend.ps1

# Telemetry simulator (new shell)
./scripts/run-sim.ps1

# Frontend (inside frontend/)
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173` for the dashboard. Backend runs at `http://127.0.0.1:8000`.

## Configuration

Copy `.env.example` to `.env` and adjust:

- `MODBUS_HOST`, `MODBUS_PORT`, `MODBUS_UNIT_ID`
- `DATASTORE_BACKEND`: `sqlite` (default) or `influx` or `mongo` (stubs in place)
- `POLL_INTERVAL_SECONDS`: PLC poll rate
- `SQLITE_PATH`: where local DB lives

## Project layout

- `backend/app/` FastAPI app (`main.py`, `control_loop.py`, `modbus_client.py`, `data_store.py`, `config.py`)
- `frontend/` React/Vite dashboard
- `sim/` telemetry simulator hitting `/ingest`
- `plc/` tag map + ladder/structured text notes (to be filled with your PLC specifics)
- `scripts/` PowerShell helpers (backend, simulator)

## Next steps

- Fill `plc/` with your tag map and Modbus register layout; update addresses in `modbus_client.py` and control rules in `control_loop.py`.
- If using InfluxDB or MongoDB, extend `DataStore` with those backends and switch `DATASTORE_BACKEND`.
- Add auth and TLS if this leaves an air-gapped network.
