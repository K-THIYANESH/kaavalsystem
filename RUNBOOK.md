**Quick Runbook**: KAAVAL (developer quickstart)
- **Purpose**: How to prepare and run the model downloader and a small reconstruction demo on Windows.

Prerequisites:
- Python 3.10+ and a virtual environment
- `git` and optionally `gh` (GitHub CLI) for PRs
- Internet connection to download model artifacts

Setup (PowerShell):
```
# create and activate venv
python -m venv .venv
& .venv\Scripts\Activate.ps1

# install dependencies
pip install -r requirements.txt
```

Download required models (will place them into `backend/models`):
```
& .venv\Scripts\python.exe backend/scripts/download_models.py --skip-images
```

Run the reconstruction demo (reads sample from `backend/datasets/sample_faces` and writes output to `backend/outputs`):
```
& .venv\Scripts\python.exe backend/scripts/run_reconstruction_demo.py
```

Notes:
- The downloader writes SHA256 sidecar files next to downloaded artifacts.
- The reconstruction demo will prefer a latent encoder (pSp/e4e) if present; otherwise it uses a fallback path and returns a synthetic reconstruction.
- If you want the assistant to run these steps for you (downloader + demo), provide consent for network downloads.

Troubleshooting:
- If `gh` prompts for authentication when creating PRs, run `gh auth login` and follow the interactive flow.
- To re-run tests:
```
& .venv\Scripts\python.exe -m pytest -q
```

Where outputs are saved:
- `backend/outputs/reconstructed_<sample>.png`
- `final_outputs.zip` (archive of `backend/outputs`)

Contact:
- If you want more automation (CI jobs, artifact publishing), tell the assistant what you prefer and I will prepare it.
RUNBOOK — KAAVAL Backend
=========================

Quick instructions to get the backend running, download models, and run tests.

Prerequisites
- Python 3.10+ and a virtual environment (`.venv` recommended).
- Install dependencies: `pip install -r requirements.txt`.

Downloading models
- The project includes a downloader at `backend/scripts/download_models.py` and a manifest at `scripts/models_manifest.json`.
- To download required models (skip sample images):

```powershell
.venv\Scripts\python.exe backend\scripts\download_models.py --skip-images
```

- The downloader will place models under `backend/models` and create a `manifest.json` there.
- The StyleGAN checkpoint is marked optional (very large). Add `--no-skip-optional` to include it.

Safe model loading
- We added `backend/app/core/model_utils.py::safe_torch_load` to prefer `weights_only=True` loads when supported.
- Loaders throughout the project call this helper to reduce unsafe unpickling. In cases where the file requires object reconstruction, the helper will allow a full load only when explicitly requested (fallback).

Running tests
- Run the full test suite:

```powershell
.venv\Scripts\python.exe -m pytest -q
```

- Run reconstruction unit test (uses demo image in `backend/datasets/demo_faces`):

```powershell
.venv\Scripts\python.exe -m pytest backend/tests/test_reconstruction_pipeline.py -q -k test_reconstructor_on_demo_image
```

CI notes
- The GitHub Actions workflow `.github/workflows/ci.yml` has two jobs:
  - `test`: runs on PRs and pushes and executes unit tests (fast, no large downloads).
  - `models-smoke`: runs only on `main` branch and downloads required models then runs a reconstruction smoke test. This keeps PRs fast while ensuring main is validated with actual models.

Where to go next
- To get faithful, input-conditioned reconstructions, integrate a latent inversion encoder (pSp/e4e) and wire it into `backend/app/ml/reconstruction/StyleGANGenerator` and the `Reconstructor` pipeline. I can scaffold and integrate this next.

Contact
- If you want specific public model URLs or to avoid downloading large binary assets in CI, provide a model store URL or GitHub release links and I can update `scripts/models_manifest.json`.

