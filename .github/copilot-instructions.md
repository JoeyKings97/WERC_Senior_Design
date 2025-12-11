# Copilot Instructions

- **Purpose**: Control/monitoring stack for cooling-tower water recovery. Backend polls PLC via Modbus, logs telemetry (SQLite by default), exposes REST/WebSocket for a React dashboard; includes simulator for local dev.

- **Architecture**

  - Backend: FastAPI (`backend/app/main.py`) with CORS open for local dev. Data flow: PLC → Modbus client → `control_loop` + `data_store` → WebSocket `/ws/telemetry` and REST.
  - PLC integration: `modbus_client.py` polls input registers (0-3 expected: humidity, temp, airflow, condensate, scaled x10) and writes coil 1 for pump enable. Update addresses/scaling to match `plc/TAG_MAP.md`.
  - Control: `control_loop.py` runs on interval `POLL_INTERVAL_SECONDS`; simple rule turns pump coil on when `condensate_rate` < target. Safety interlocks remain on PLC—do not move them to software.
  - Data: `data_store.py` writes to SQLite table `telemetry`; stubs for Influx/Mongo ready when `DATASTORE_BACKEND` is switched. WebSocket streams from an in-memory queue fed by PLC poll or `/ingest` pushes.
  - Frontend: React/Vite (`frontend/src/App.jsx`) consumes `/ws/telemetry`, shows KPIs, and calls `/control/enable|disable`. Styles in `frontend/src/styles.css`.
  - Simulator: `sim/simulator.py` posts random telemetry to `/ingest` every 2s; meant for no-PLC dev.

- **Config & secrets**

  - Copy `.env.example` → `.env`. Key vars: `MODBUS_HOST`, `MODBUS_PORT`, `MODBUS_UNIT_ID`, `POLL_INTERVAL_SECONDS`, `DATASTORE_BACKEND` (`sqlite|influx|mongo`), `SQLITE_PATH`, optional Influx/Mongo creds.
  - Default ports: backend 8000, WS at `/ws/telemetry`, frontend dev 5173.

- **Run workflows (PowerShell, Windows)**

  - Backend dev: `./scripts/run-backend.ps1` (creates venv, installs deps, runs uvicorn with reload).
  - Simulator: `./scripts/run-sim.ps1` (same venv, installs httpx, pushes telemetry).
  - Frontend dev: `cd frontend; npm install; npm run dev`.

- **Patterns & conventions**

  - Keep PLC safety and interlocks in ladder/ST; backend only toggles defined coils/registers.
  - Telemetry scaling currently divides by 10 after Modbus read—align with PLC scaling.
  - WebSocket feed sources from `DataStore.live_queue`; any ingest path should push there to keep UI live.
  - Extend `DataStore` for Influx/Mongo by adding write/read branches keyed on `datastore_backend`.
  - For new control logic, keep setpoint math in `ControlLoop._apply_control`; avoid blocking calls inside the loop.

- **Testing/dev tips**

  - Without PLC: run backend + simulator + frontend; verify dashboard updates and control toggles.
  - With PLC: set real addresses in `modbus_client.py` and tag map; validate reads before enabling writes.
  - If you add auth/TLS, ensure CORS/WebSocket settings stay aligned with frontend origin.

- **Key files**: `backend/app/main.py`, `config.py`, `modbus_client.py`, `control_loop.py`, `data_store.py`; `frontend/src/App.jsx`, `frontend/src/styles.css`; `scripts/run-backend.ps1`, `scripts/run-sim.ps1`; `plc/TAG_MAP.md`.
