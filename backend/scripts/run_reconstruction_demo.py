#!/usr/bin/env python3
"""Run a small reconstruction demo using the project's Reconstructor.

Loads a sample face from `backend/datasets/sample_faces` and writes a
reconstructed output to `backend/outputs/reconstructed_demo.png`.
"""
from pathlib import Path
import sys
import cv2
import numpy as np

# Ensure project root is on sys.path so `app` package is importable
repo_root = Path(__file__).parent.parent.parent
# Add `backend` package directory to sys.path so `app` package resolves
backend_pkg = repo_root / "backend"
sys.path.insert(0, str(backend_pkg))

from app.ml.reconstruction.reconstructor import Reconstructor
from app.core.config import settings


def main():
    sample_dir = repo_root / "backend" / "datasets" / "sample_faces"
    out_dir = repo_root / "backend" / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    imgs = list(sample_dir.glob("*.jpg")) + list(sample_dir.glob("*.png"))
    if not imgs:
        print("No sample images found in", sample_dir)
        return 1

    img_path = imgs[0]
    img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
    if img is None:
        print("Failed to load sample image:", img_path)
        return 1

    recon = Reconstructor()
    out_img, conf = recon.reconstruct(img)

    out_path = out_dir / f"reconstructed_{img_path.stem}.png"
    cv2.imwrite(str(out_path), out_img)
    print(f"Wrote reconstructed image to: {out_path} (confidence={conf:.2f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
