Release Notes — Debug & Model Safety Pass
======================================

Summary
- Completed a scoped debugging pass to make the backend runnable and safer to use with model artifacts.

Key changes
- Centralized safe model loading in `backend/app/core/model_utils.py`.
- Implemented reconstruction scaffolding and a StyleGAN wrapper that attempts safe loads first.
- Added a model manifest and downloader to automate reproducible setups.
- Updated scripts to avoid direct `torch.load` unpickling where feasible.
- Added CI job to validate models on `main` only (keeps PRs fast).

How this affects you
- Pull latest changes, create and activate `.venv`, install requirements, then run the downloader to get models for full functionality.

Next work (recommended)
- Integrate a latent inversion encoder (pSp/e4e) to enable true input-conditioned GAN reconstructions.
- Migrate `pydantic` validators to v2 `field_validator` API to remove deprecation warnings.
- Optionally host model artifacts in a release or object store and add checksums to the manifest for CI reproducibility.

