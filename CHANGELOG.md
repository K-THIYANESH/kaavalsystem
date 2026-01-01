# CHANGELOG

All notable changes made by the assistant during the debug/modernization effort.

Unreleased
- Added `backend/app/core/model_utils.py` with `safe_torch_load` to prefer `weights_only` loads and centralize torch.load behavior.
- Implemented `Reconstructor` scaffolding with `StyleGANGenerator` and GFPGAN fallbacks (`backend/app/ml/reconstruction/*`).
- Added `scripts/models_manifest.json` and `backend/scripts/download_models.py` to download required model weights.
- Rewrote several scripts to use `safe_torch_load` rather than direct `torch.load` where possible (`backend/scripts/*`).
- Added `backend/tests/test_reconstruction_pipeline.py` (unit test for reconstruction pipeline) and ensured tests pass locally.
- Updated GitHub Actions workflow `.github/workflows/ci.yml` to add a `models-smoke` job (runs on `main`) that downloads models and runs a model-enabled smoke test.
- Fixed multiple import/formatting issues (removed markdown fences that broke imports) and OS-specific logging/encoding issues on Windows.

Notes
- The project still contains warnings (pydantic v2 migration, and torch unpickling warnings when full loads happen). These are documented in `RUNBOOK.md` with suggested remediations.

