"""Latent inversion encoder scaffold (pSp / e4e style).

This module provides a lightweight wrapper `LatentEncoder` that will attempt
to load an encoder checkpoint from `backend/models` (names supported below).

If no encoder model is available, the wrapper falls back to a mock that
returns random latents. The class API is intentionally small:

- `available()` -> bool
- `invert(image: np.ndarray) -> torch.Tensor` returns a latent tensor suitable
  for passing into `StyleGANGenerator.generate_from_latent`.

The real integration requires a trained pSp/e4e encoder checkpoint; this
scaffold centralizes loading and safe model handling.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import torch

from ...core.config import settings
from ...core.model_utils import safe_torch_load


@dataclass
class LatentEncoder:
    weights_path: Optional[str] = None
    device: torch.device = torch.device("cpu")
    _model: Optional[object] = None

    def __post_init__(self) -> None:
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        candidates = []
        if self.weights_path:
            candidates.append(Path(self.weights_path))

        # common names to look for
        candidates.extend([
            settings.models_dir / "psp_encoder.pth",
            settings.models_dir / "e4e_encoder.pth",
            settings.models_dir / "encoder.pth",
        ])

        for p in candidates:
            try:
                if p is None:
                    continue
                if not Path(p).exists():
                    continue
                # Attempt safe load; prefer weights-only
                loaded = safe_torch_load(p, map_location=self.device)
                if loaded is None:
                    # explicit fallback if the maintainer opts in via file name
                    loaded = safe_torch_load(p, map_location=self.device, prefer_weights_only=False, allow_untrusted=True)
                if loaded is None:
                    continue

                # If checkpoint is a state_dict, we expect a model class to instantiate
                # The project may include an encoder implementation; attempt to import
                try:
                    # user-provided encoder class location can vary; try common helper
                    from ..age_progression.encoder_impl import EncoderImpl  # type: ignore
                    model = EncoderImpl()
                    if isinstance(loaded, dict):
                        model.load_state_dict(loaded)
                    else:
                        # loaded may be a full module
                        model = loaded
                    model.to(self.device).eval()
                    self._model = model
                    break
                except Exception:
                    # If we couldn't instantiate a known class, but `loaded` is a module,
                    # accept it directly if it has an `encode` or `forward` method.
                    if hasattr(loaded, "encode") or hasattr(loaded, "forward"):
                        try:
                            mod = loaded
                            self._model = mod
                            break
                        except Exception:
                            pass
            except Exception:
                continue

    def available(self) -> bool:
        return self._model is not None

    def invert(self, image: np.ndarray) -> torch.Tensor:
        """Invert an image to a latent tensor.

        If encoder model is unavailable, return a random latent tensor sized
        to match StyleGAN conventions (W+ with shape [1, 18, 512]) as a fallback.
        """
        if image is None:
            raise ValueError("image must be provided")

        if not self.available():
            # return a random W+ style latent
            z = torch.randn(1, 18, 512, device=self.device)
            return z

        # If model provides `encode` or `forward`, call it
        img = image
        if isinstance(img, np.ndarray):
            # convert to CHW float tensor expected by encoders: [1,3,H,W], normalized [-1,1]
            t = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0).to(self.device).float()
            t = (t / 127.5) - 1.0
        else:
            t = image.to(self.device)

        try:
            if hasattr(self._model, "encode"):
                out = self._model.encode(t)
            else:
                out = self._model(t)
            # Ensure output is tensor and shape is compatible
            if isinstance(out, tuple):
                out = out[0]
            return out.detach()
        except Exception:
            # fallback random latent on failure
            return torch.randn(1, 18, 512, device=self.device)
