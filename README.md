# Cooling Tower Water Recovery — Control/Monitoring Stack

End-to-end stack to monitor and control a cooling‑tower vapor recovery retrofit. Backend polls a PLC via Modbus (or ingests simulator data), persists telemetry (SQLite by default), and streams live updates to a React dashboard. Designed for local development now and easy hardware integration later.

## Quick Start (Windows PowerShell)

Run everything

```powershell
./scripts/run-all.ps1
```

- Dashboard: <http://localhost:5173> (Vite may fall back to 5174)
- Backend: <http://localhost:8000>

Run individually

```powershell
# Backend
./scripts/run-backend.ps1

# Telemetry simulator (new shell)
./scripts/run-sim.ps1

# Frontend
cd frontend
npm install
npm run dev
```

## Configuration

Copy `.env.example` → `.env` and adjust:

- `MODBUS_HOST`, `MODBUS_PORT`, `MODBUS_UNIT_ID`
- `POLL_INTERVAL_SECONDS` (poll rate)
- `DATASTORE_BACKEND` = `sqlite|influx|mongo` (default `sqlite`)
- `SQLITE_PATH` (default `./data/telemetry.db`)
- Influx (optional): `INFLUX_URL`, `INFLUX_TOKEN`, `INFLUX_ORG`, `INFLUX_BUCKET`

## Architecture Overview

- Backend: FastAPI app in `backend/app/main.py` with REST (`/health`, `/config`, `/metrics`, `/ingest`) and WebSocket (`/ws/telemetry`). Startup/shutdown manage `DataStore` and `ControlLoop` lifecycles.
- PLC Integration: Async Modbus TCP client (`backend/app/modbus_client.py`) reads input registers and writes pump coil. Addresses/scaling to match `plc/TAG_MAP.md` (current scaling ÷10).
- Control Loop: `backend/app/control_loop.py` runs every `POLL_INTERVAL_SECONDS`, logs telemetry, and applies a simple rule (enable pump when `condensate_rate` < target). Keep PLC safety interlocks on hardware.
- Data Store: `backend/app/data_store.py` persists telemetry to SQLite and streams via an in‑memory queue to WebSocket. InfluxDB backend is implemented and can be enabled via env.
- Frontend: React/Vite (`frontend/src/App.jsx`) consumes `/ws/telemetry`, shows KPIs, and calls `/control/enable|disable`.
- Simulator: `sim/simulator.py` posts random telemetry to `/ingest` for no‑PLC dev.

## PLC Setup (when hardware is available)

- Fill `plc/TAG_MAP.md` with real Modbus tags, addresses, and scaling.
- Update `backend/app/modbus_client.py` to match your PLC map.
- Validate reads in the dashboard, then enable coil writes for control.

## Development Notes

- WebSocket live feed sources from `DataStore.live_queue`; any ingest path should push there.
- SQLite parent folder is auto‑created; DB file at `./data/telemetry.db`.
- CORS is open for local dev; restrict origins for production.
- If adding auth/TLS, align frontend origin and WebSocket settings.

## GitHub Workflow

- Use `./scripts/push-to-github.ps1` to initialize and push.
- `.gitignore` excludes venv, data files, node_modules, logs, and `.env`.

## Next Steps

- Integrate PLC addresses/scaling; confirm telemetry alignment.
- Expand control logic (multi‑stage condenser, humidity setpoints, alarms).
- Add unit tests and GitHub Actions.
