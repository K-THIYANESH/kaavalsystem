Developer Quickstart — KAAVAL AI System

This file describes the minimal steps to verify environment, install dependencies, and run the services locally.

Prerequisites
- Windows 10/11 (PowerShell available)
- Git (optional)
- Python 3.10 (recommended) — the project uses a local `.venv`
- Some model files are large (RetinaFace, ArcFace, GFPGAN, StyleGAN) — ensure you have bandwidth and disk space.

Verify virtual environment
1. Ensure `.venv` exists at the project root. If it does not, the startup scripts will create and populate it.

Check installed packages (inside project folder)

PowerShell:

```powershell
# From project root
& .\.venv\Scripts\python.exe -m pip list
```

If you don't have a `.venv` yet, create and install dependencies:

```powershell
# Create venv
python -m venv .venv
# Activate
& .\.venv\Scripts\Activate.ps1
# Install backend dependencies
python -m pip install -r backend\requirements.txt
```

Run the project

Option 1: Unified startup (recommended)

```powershell
# From project root
# This script will create .venv (if missing), install backend requirements, start the frontend http server and the backend uvicorn server
.\start_project.ps1
```

Option 2: Start backend only

```powershell
# Activate venv first
& .\.venv\Scripts\Activate.ps1
# Start backend (development)
& .\backend\start_backend.ps1
# or
python .\backend\start_server.py
```

Option 3: Serve frontend only (static files)

```powershell
# Serve frontend on port 8001 (frontend must be in project\frontend)
& .\.venv\Scripts\python.exe -m http.server 8001 --directory "frontend"
```

Smoke checks
- Backend health: GET http://127.0.0.1:8000/healthz
- API docs: http://127.0.0.1:8000/docs
- Frontend UI: http://127.0.0.1:8001

Notes & Next steps
- Many ML pipelines include placeholders (reconstruction, age progression, detectors). These are intentionally left as stubs and must be connected to real model inference code for production.
- `backend/models/manifest.json` references the models. Ensure the files listed there exist.
- Before running heavy inference, confirm `onnxruntime`/`torch` GPU installations and drivers on your machine.

If you'd like, I can:
- Run `pip list` and install missing packages now.
- Start the services and perform smoke tests.
- Produce a cleanup proposal listing candidate unused files for removal.

