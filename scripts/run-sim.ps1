$ErrorActionPreference = "Stop"
if (!(Test-Path .venv)) { python -m venv .venv }
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install httpx
python sim\simulator.py
