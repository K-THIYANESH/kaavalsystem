"""StyleGAN generator wrapper using the bundled stylegan2-ada-pytorch code if present.

This loader attempts multiple strategies to load a StyleGAN checkpoint:
- Use the repository's `legacy.load_network_pkl` if available (recommended for TF/legacy pickles).
- Attempt `torch.load(..., weights_only=True)` to safely load state_dicts (PyTorch 2.x).
- Attempt `torch.load(...)` as a last resort (unsafe unpickling warning).

The wrapper exposes a `generate_from_z` method that returns a HxWxC uint8 BGR image.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import torch
import cv2

from ...core.config import settings
from ...core.model_utils import safe_torch_load


@dataclass
class StyleGANGenerator:
    weights_path: str | None = None
    device: torch.device = torch.device("cpu")
    _net: Optional[object] = None

    def __post_init__(self) -> None:
        if not self.weights_path:
            return

        path = Path(self.weights_path)
        if not path.is_absolute():
            path = settings.project_root / path
        if not path.exists():
            path = settings.models_dir / path.name
        if not path.exists():
            return

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # 1) Try legacy loader from bundled stylegan2-ada-pytorch
        try:
            import backend.external.stylegan2_ada_pytorch.legacy as legacy  # type: ignore
        except Exception:
            # try alternative import path used by repository
            try:
                from backend.external.stylegan2_ada_pytorch import legacy  # type: ignore
            except Exception:
                legacy = None

        if legacy is not None:
            try:
                # legacy.load_network_pkl accepts file-like or path
                with open(path, 'rb') as f:
                    data = legacy.load_network_pkl(f)
                # data expected to be dict with G, D, G_ema
                G_ema = data.get('G_ema') or data.get('g_ema') or data.get('G')
                if G_ema is not None:
                    self._net = G_ema.eval().requires_grad_(False).to(self.device)
                    return
            except Exception:
                pass

        # 2) Try torch.load weights-only (safe) if supported
        try:
            obj = safe_torch_load(path, map_location=self.device)
            if obj is not None:
                # If obj is a dict of tensors (state_dict), we cannot instantiate arch.
                # But some checkpoints are full data dicts with modules; try to find G_ema
                if isinstance(obj, dict):
                    for k in ('G_ema', 'g_ema', 'G'):
                        if k in obj and hasattr(obj[k], 'eval'):
                            self._net = obj[k].eval().requires_grad_(False).to(self.device)
                            return
                # If obj itself is a module
                if hasattr(obj, 'eval'):
                    self._net = obj.eval().requires_grad_(False).to(self.device)
                    return
        except Exception:
            # If safe load failed, continue to last-resort plain torch.load below
            pass

        # 3) Last resort: plain torch.load (unsafe unpickling)
        try:
            # Request an explicit untrusted load only when necessary
            obj = safe_torch_load(path, map_location=self.device, prefer_weights_only=False, allow_untrusted=True)
            # Accept module or dict with G_ema
            if isinstance(obj, dict):
                G_ema = obj.get('G_ema') or obj.get('g_ema') or obj.get('G')
                if G_ema is not None and hasattr(G_ema, 'eval'):
                    self._net = G_ema.eval().requires_grad_(False).to(self.device)
                    return
            if hasattr(obj, 'eval'):
                self._net = obj.eval().requires_grad_(False).to(self.device)
                return
        except Exception:
            self._net = None

    def available(self) -> bool:
        return self._net is not None

    def generate_from_z(self, z: Optional[torch.Tensor] = None, truncation_psi: float = 0.7) -> np.ndarray:
        """Generate an image from latent z (torch tensor, shape [1, z_dim]) or random.

        Returns an HxWxC uint8 BGR image.
        """
        if self._net is None:
            raise RuntimeError("StyleGAN generator not loaded")

        # Prepare latent
        if z is None:
            z = torch.randn(1, 512, device=self.device)
        else:
            z = z.to(self.device)

        try:
            # Many StyleGAN wrappers expect mapping + synthesis; we try common call signatures
            with torch.no_grad():
                try:
                    img_tensor = self._net(z, None, truncation_psi=truncation_psi, noise_mode='const')
                except TypeError:
                    # Alternative call
                    img_tensor = self._net(z, truncation_psi=truncation_psi, noise_mode='const')

            # img_tensor expected in NCHW, range [-1, 1] or [0,255]
            if isinstance(img_tensor, tuple):
                img_tensor = img_tensor[0]

            img = img_tensor.detach().cpu()
            if img.max() <= 1.0:
                img = (img * 127.5 + 128).clamp(0, 255).to(torch.uint8)
            else:
                img = img.clamp(0, 255).to(torch.uint8)

            # Convert to HWC BGR
            if img.ndim == 4:
                img = img[0]
            img = img.permute(1, 2, 0).numpy()
            # Convert RGB to BGR for OpenCV saving consistency if needed
            try:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            except Exception:
                pass
            return img
        except Exception as e:
            raise RuntimeError(f"StyleGAN generation failed: {e}")

    def generate_from_latent(self, latent: torch.Tensor, truncation_psi: float = 0.7) -> np.ndarray:
        """Generate from a latent that's already in W or W+ space.

        This method attempts common call patterns for StyleGAN generator objects:
        - If the module exposes `synthesis` or `synthesis` under `.synthesis`, call it.
        - If the module accepts (w, None) or (w) directly, call it.

        The method returns an HxWxC uint8 BGR image on success.
        """
        if self._net is None:
            raise RuntimeError("StyleGAN generator not loaded")

        w = latent.to(self.device)
        try:
            with torch.no_grad():
                # Try common synthetic APIs
                if hasattr(self._net, "synthesis"):
                    img_tensor = self._net.synthesis(w)
                else:
                    try:
                        img_tensor = self._net(w, None, truncation_psi=truncation_psi, noise_mode='const')
                    except TypeError:
                        img_tensor = self._net(w, truncation_psi=truncation_psi, noise_mode='const')

                if isinstance(img_tensor, tuple):
                    img_tensor = img_tensor[0]

                img = img_tensor.detach().cpu()
                if img.max() <= 1.0:
                    img = (img * 127.5 + 128).clamp(0, 255).to(torch.uint8)
                else:
                    img = img.clamp(0, 255).to(torch.uint8)

                if img.ndim == 4:
                    img = img[0]
                img = img.permute(1, 2, 0).numpy()
                try:
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                except Exception:
                    pass
                return img

        except Exception as e:
            raise RuntimeError(f"StyleGAN generation from latent failed: {e}")
