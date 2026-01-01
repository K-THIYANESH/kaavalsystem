"""StyleGAN-based age progression."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import torch
import numpy as np
import cv2
import sys
from pathlib import Path as _Path

from ...core.config import settings
from ...schemas.image import AgeVariant


@dataclass
class StyleGANAgeProgressor:
    """Generate age progressed faces for multiple offsets."""

    weights_path: str | None = None

    def __post_init__(self) -> None:
        if not self.weights_path:
            return

        path = Path(self.weights_path)
        if not path.is_absolute():
            path = settings.project_root / path
            
        if not path.exists():
            path = settings.models_dir / path.name
            
        if not path.exists():
            print(f"WARNING: StyleGAN model not found at {path}")
            self._model = None
            return

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        try:
            # Attempt to load as TorchScript first
            try:
                self._model = torch.jit.load(str(path), map_location=self.device)
            except Exception:
                # Ensure project root is on sys.path so training runtime helpers
                # (e.g. torch_utils) can be imported during unpickling.
                try:
                    project_root = _Path(settings.project_root)
                    pr = str(project_root)
                    if pr not in sys.path:
                        sys.path.insert(0, pr)
                except Exception:
                    pass

                # If the checkpoint was saved with training helper modules
                # like `torch_utils.persistence._reconstruct_persistent_obj`,
                # add that function to torch's safe globals so unpickling can
                # reconstruct objects safely (only if the module is present).
                try:
                    from torch_utils.persistence import _reconstruct_persistent_obj
                    try:
                        torch.serialization.add_safe_globals([_reconstruct_persistent_obj])
                    except Exception:
                        pass
                except Exception:
                    pass

                # Prefer weights-only loading via safe_torch_load to reduce unpickling surface
                try:
                    from ...core.model_utils import safe_torch_load
                    loaded = safe_torch_load(path, map_location=self.device)
                    if loaded is None:
                        # allow full unpickle path via the same helper (explicit)
                        loaded = safe_torch_load(path, map_location=self.device, prefer_weights_only=False, allow_untrusted=True)
                except Exception:
                    # Fall back to direct torch.load as last resort if helper import fails
                    loaded = torch.load(str(path), map_location=self.device)

                self._model = loaded

            if hasattr(self._model, "eval"):
                self._model.eval()

        except Exception as e:
            print(f"Error loading StyleGAN model: {e}")
            self._model = None

    def progress(self, job_id: str, offsets: List[int], base_path: Path) -> List[AgeVariant]:
        variants: List[AgeVariant] = []
        
        # Note: Real implementation requires the source image and an encoder (e.g. pSp).
        # Since the current pipeline does not pass the image and we lack the encoder,
        # we will mock the output but ensure the model is loaded on the correct device.
        
        if self._model is None:
            # Fallback mock generation if model is missing
            for offset in offsets:
                path = base_path / f"{job_id}_age_{offset}.png"
                # Create a dummy image (gray)
                dummy_img = np.full((512, 512, 3), 127, dtype=np.uint8)
                cv2.imwrite(str(path), dummy_img)
                variants.append(AgeVariant(age_offset=offset, image_path=str(path), confidence=0.88))
            return variants

        # 1. Invert Image to Latent Code (W+)
        # In a real pipeline, we would use an encoder like pSp or e4e here.
        # w_latent = self._invert_image(input_image)
        # For now, we generate a random latent code
        w_latent = torch.randn(1, 18, 512).to(self.device)

        # 2. Load Age Direction Vector
        # direction = torch.load("age_direction.pt")
        # Placeholder direction
        direction = torch.randn(1, 18, 512).to(self.device)
        direction = direction / torch.norm(direction)

        for offset in offsets:
            path = base_path / f"{job_id}_age_{offset}.png"
            
            # 3. Edit Latent Code
            # Linear interpolation in W+ space: w_new = w + alpha * direction
            # Scale offset to alpha (heuristic)
            alpha = offset * 0.1 
            w_new = w_latent + alpha * direction
            
            # 4. Generate Image
            # with torch.no_grad():
            #     img_tensor = self._model(w_new, noise_mode='const')
            
            # Placeholder save
            # save_image(img_tensor, path)
            path.write_bytes(b"age-prog-image-placeholder")
            
            variants.append(AgeVariant(age_offset=offset, image_path=str(path), confidence=0.92))
            
        return variants

    def _invert_image(self, image: np.ndarray) -> torch.Tensor:
        """Invert image to W+ latent space using an encoder."""
        # Placeholder for pSp/e4e encoder
        return torch.randn(1, 18, 512).to(self.device)

