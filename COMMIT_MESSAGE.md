Commit summary: Debug & reconstruction feature completion

This commit includes:
- Centralized safe model loading via `backend/app/core/model_utils.py`.
- Reconstructor scaffolding with StyleGAN and GFPGAN fallbacks (`backend/app/ml/reconstruction/*`).
- Latent inversion encoder scaffold (`backend/app/ml/reconstruction/encoder.py`) and integration.
- StyleGAN wrapper improvements to accept latents (`generate_from_latent`).
- Model downloader and manifest (`scripts/models_manifest.json`, `backend/scripts/download_models.py`) with checksum computation.
- CI updates: `.github/workflows/ci.yml` adds a `models-smoke` job that runs on `main`.
- Various script fixes (removed markdown fences, safe loader usage) and docs (`RUNBOOK.md`, `CHANGELOG.md`, `RELEASE_NOTES.md`).

Files changed: see git diff. Key files:
- backend/app/core/model_utils.py
- backend/app/ml/reconstruction/*
- backend/scripts/download_models.py
- scripts/models_manifest.json
- .github/workflows/ci.yml
- RUNBOOK.md, CHANGELOG.md, RELEASE_NOTES.md

Notes:
- `safe_torch_load` avoids untrusted pickle unwrapping unless explicitly allowed (`allow_untrusted=True`).
- The encoder scaffold requires a real pSp/e4e checkpoint to produce faithful reconstructions; populate `scripts/models_manifest.json` with a public URL and checksum to enable CI download.

