KAAVAL - Debug & Runbook
=========================

Quick steps to validate and run the backend locally after the fixes applied by the debugging sweep.

- Ensure virtualenv activated and dependencies installed:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- Verify reconstruction model availability (mandatory by default):

Place one of the following model files into `backend/models`:

- `gfpgan.pth` (GFPGAN weights)
- `stylegan2_age.pt` or `stylegan2-ada.pth` / `.pkl` (StyleGAN generator)

- Quick check script:

```powershell
.venv\Scripts\python.exe scripts\check_reconstruction.py
```

- Run tests:

```powershell
.venv\Scripts\python.exe -m pytest -q
```

- Run the API (development):

```powershell
uvicorn backend.app.main:app --reload
```

Notes
- The app now forces file handlers and stdout/stderr to UTF-8 where possible to avoid Windows encoding errors.
- Pydantic v2 compatibility shims were added for field validators; the project still supports pydantic v1.
- If you prefer the application to start even without a reconstruction model, set `REQUIRE_RECONSTRUCTION_MODEL=false` in the `.env` file or modify `settings.require_reconstruction_model`.
