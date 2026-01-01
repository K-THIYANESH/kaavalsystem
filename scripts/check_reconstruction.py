"""Small script to validate the reconstruction backend is available."""

from pathlib import Path
import sys

sys.path.insert(0, "backend")

from app.ml.reconstruction.reconstructor import Reconstructor
from app.core.config import settings


def main():
    print("Models dir:", settings.models_dir)
    recon = Reconstructor()
    print("Reconstructor available:", recon.available())
    if not recon.available():
        print("No reconstruction model detected. Look for gfpgan.pth or stylegan files in models dir.")
    else:
        print("At least one reconstruction backend detected (StyleGAN/GFPGAN).")


if __name__ == '__main__':
    main()
