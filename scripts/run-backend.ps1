$ErrorActionPreference = "Stop"

# Prefer Python 3.12 for FastAPI/Pydantic compatibility; fallback to current python if py -3.12 not available
$py312 = "py -3.12"
try {
	$pyver = (& py --list 2>$null) -join "\n"
	if ($pyver -notmatch "3\.12") { throw "py 3.12 not found" }
} catch {
	Write-Host "Python 3.12 via 'py' launcher not found; falling back to current 'python'." -ForegroundColor Yellow
	$py312 = "python"
}

# Hard guard: abort if current interpreter is 3.14+ (pydantic-core wheels not available)
$currentVersion = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ([version]$currentVersion -ge [version]"3.14") {
	Write-Error "Detected Python $currentVersion in active shell. Please install Python 3.12 and rerun: 'py -3.12 -m venv .venv'"
	exit 1
}

if (!(Test-Path .venv)) { & $py312 -m venv .venv }
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -r backend\requirements.txt

# Copy env if missing
if (!(Test-Path .env) -and (Test-Path .env.example)) { Copy-Item .env.example .env }

# Use module invocation to avoid PATH issues
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
