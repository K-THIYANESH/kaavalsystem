"""Reconstruction model loader and wrapper.

This module attempts to load a forensic reconstruction model. If a heavy
GAN-based reconstructor isn't available it falls back to GFPGAN-based
restoration or OpenCV inpainting as a safe fallback so the API can return
usable outputs for the rest of the system.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np
import torch

from ...core.config import settings

try:
    from ..restoration.gfpgan import GFPGANRestorer
except Exception:
    GFPGANRestorer = None

try:
    from .stylegan_generator import StyleGANGenerator
except Exception:
    StyleGANGenerator = None
 
try:
    from .encoder import LatentEncoder
except Exception:
    LatentEncoder = None


@dataclass
class Reconstructor:
    """High-level reconstructor used by pipelines.

    This class tries the following in order:
    - Use a dedicated reconstruction model (StyleGAN / custom generator) if present
    - Use GFPGAN (if installed and model available)
    - Use OpenCV inpainting as a last-resort fallback
    """

    device: torch.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _gfpgan: Optional[GFPGANRestorer] = None
    _stylegan: Optional[StyleGANGenerator] = None
    _encoder: Optional[LatentEncoder] = None

    def __post_init__(self) -> None:
        # Try to detect and load a StyleGAN-like checkpoint in models dir
        stylegan_candidates = [
            settings.models_dir / "stylegan2_age.pt",
            settings.models_dir / "stylegan2-ada.pth",
            settings.models_dir / "stylegan2-ada.pkl",
            settings.models_dir / "stylegan2-ada.pkl",
        ]

        for p in stylegan_candidates:
            if p.exists() and StyleGANGenerator is not None:
                try:
                    self._stylegan = StyleGANGenerator(weights_path=str(p))
                    if self._stylegan.available():
                        break
                    else:
                        self._stylegan = None
                except Exception:
                    self._stylegan = None

        # Initialize GFPGAN restorer if available
        if GFPGANRestorer is not None:
            # Try both explicit name and generic model path
            gfpgan_path = settings.models_dir / "gfpgan.pth"
            if gfpgan_path.exists():
                try:
                    self._gfpgan = GFPGANRestorer(weights_path=str(gfpgan_path))
                except Exception:
                    self._gfpgan = GFPGANRestorer(weights_path=None)
            else:
                # allow user to put weight at project root models dir
                try:
                    self._gfpgan = GFPGANRestorer(weights_path=None)
                except Exception:
                    self._gfpgan = None

        # Initialize latent encoder if available
        if LatentEncoder is not None:
            encoder_candidates = [
                settings.models_dir / "psp_encoder.pth",
                settings.models_dir / "e4e_encoder.pth",
                settings.models_dir / "encoder.pth",
            ]
            for p in encoder_candidates:
                try:
                    if p.exists():
                        self._encoder = LatentEncoder(weights_path=str(p))
                        if self._encoder.available():
                            break
                        else:
                            self._encoder = None
                except Exception:
                    self._encoder = None

    def available(self) -> bool:
        """Return True if any reconstruction backend is available."""
        return (
            (self._stylegan is not None and self._stylegan.available())
            or (self._gfpgan is not None and getattr(self._gfpgan, "_restorer", None) is not None)
        )

    def reconstruct(self, image: np.ndarray, mask: Optional[np.ndarray] = None) -> Tuple[np.ndarray, float]:
        """Reconstruct / restore an image; return (image, confidence).

        This method prefers GAN-based reconstruction when available, falls
        back to GFPGAN and finally OpenCV inpainting.
        """
        # If stylegan is available, prefer encoder-conditioned generation
        if self._stylegan is not None and self._stylegan.available():
            try:
                if self._encoder is not None and self._encoder.available():
                    try:
                        latent = self._encoder.invert(image)
                        img = self._stylegan.generate_from_latent(latent)
                        return img, 0.98
                    except Exception:
                        # If encoder fails, fall back to random generation
                        pass

                # Fallback: random latent generation
                img = self._stylegan.generate_from_z()
                return img, 0.75
            except Exception:
                pass

        # Try GFPGAN
        if self._gfpgan is not None and getattr(self._gfpgan, "_restorer", None) is not None:
            try:
                import tempfile

                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
                    tmp_path = Path(tf.name)
                    cv2.imwrite(str(tmp_path), image)

                out_path, _attrs = self._gfpgan.restore(tmp_path)
                restored = cv2.imread(str(out_path), cv2.IMREAD_COLOR)
                if restored is None:
                    return image.copy(), 0.5
                return restored, 0.9
            except Exception:
                pass

        # Final fallback: simple OpenCV inpainting if mask provided
        try:
            if mask is not None:
                inpainted = cv2.inpaint(image, (mask.astype("uint8") * 255).astype("uint8"), 3, cv2.INPAINT_TELEA)
                return inpainted, 0.6
        except Exception:
            pass

        # Nothing available: return input copy with low confidence
        return image.copy(), 0.2
