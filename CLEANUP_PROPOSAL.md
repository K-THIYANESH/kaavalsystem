KAAVAL — Cleanup Proposal

This file lists candidate files and folders for cleanup or archiving. I will not delete anything without your confirmation.

Candidates

1) Duplicate GFPGAN weights
- Files: `backend/models/gfpgan.pth` and `backend/models/GFPGANv1.4.pth`
- Reason: They appear to be duplicates (same model family). `manifest.json` references `gfpgan.pth`. If `GFPGANv1.4.pth` is an older copy, consider removing or archiving it to save disk space.
- Action: Verify file sizes and contents; keep one canonical name matching `manifest.json`.

2) `.venv` inside project root
- Location: `.venv/`
- Reason: Large, contains installed packages. Keep for local development. If you want to reduce repository size, do not commit `.venv` to version control and consider recreating on target machines.
- Action: Keep locally; add to .gitignore if not present.

3) `embeddings_output/` large per-user files
- Location: `backend/embeddings_output/`
- Reason: Contains many .npy and .json embedding files. Useful for demo but may be large. Consider compressing or archiving if not actively used.
- Action: Archive older embeddings; keep a single `demo_embeddings` set for quick testing.

4) `reports/` and `logs/` historic files
- Location: `backend/reports/`, `backend/logs/`
- Reason: May contain generated reports and logs that can be archived to reduce clutter.
- Action: Rotate logs, compress old reports.

5) `backend/scripts/download_faces.py` and other placeholder scripts
- Reason: These are helpful for demo data but flagged as placeholder. Keep in `scripts/` but mark clearly or move to `scripts/placeholder/`.
- Action: Move placeholder scripts to `scripts/placeholder/` if you want to declutter.

6) Tests with `pass` or incomplete
- Location: `backend/tests/verify_video_pipeline.py` and similar
- Reason: Tests are stubs and may give a false sense of coverage.
- Action: Either implement meaningful tests or remove test stubs.

Notes
- I will not delete or move any files until you confirm. If you approve, I can archive duplicates into `backend/archive/` and remove them from active dirs.

Would you like me to:
- (A) Archive the duplicate GFPGAN file into `backend/archive/` now.
- (B) Produce a script to compress `embeddings_output/` and move older files to `backend/archive/`.
- (C) Implement .gitignore updates and small housekeeping changes now.
- (D) Do nothing yet — continue wiring/placeholders fixes.

Reply with choice or provide instructions.
