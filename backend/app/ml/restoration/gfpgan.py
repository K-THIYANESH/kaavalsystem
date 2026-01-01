"""Wrapper for GFPGAN-based restoration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import torch

from ...core.config import settings
from ...schemas.image import RestorationAttributes

try:
    from gfpgan import GFPGANer
except ImportError:
    GFPGANer = None


@dataclass
class GFPGANRestorer:
    """Restore degraded faces and return metadata."""

    weights_path: str | None = None

    def __post_init__(self) -> None:
        if GFPGANer is None:
            print("WARNING: gfpgan package not installed.")
            self._restorer = None
            return

        if not self.weights_path:
            return

        path = Path(self.weights_path)
        if not path.is_absolute():
            path = settings.project_root / path
            
        if not path.exists():
            path = settings.models_dir / path.name
            
        if not path.exists():
            print(f"WARNING: GFPGAN model not found at {path}")
            self._restorer = None
            return

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        try:
            self._restorer = GFPGANer(
                model_path=str(path),
                upscale=1,
                arch="clean",
                channel_multiplier=2,
                bg_upsampler=None,
                device=device
            )
        except Exception as e:
            print(f"Error loading GFPGAN model: {e}")
            self._restorer = None

    def restore(self, image_path: Path) -> tuple[Path, RestorationAttributes]:
        output_path = image_path.with_name(image_path.stem + "_restored.png")
        
        if self._restorer is None:
            # Fallback if model failed to load
            output_path.write_bytes(image_path.read_bytes())
            return output_path, RestorationAttributes()

        try:
            img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError(f"Could not read image: {image_path}")

            # Restore
            _, _, restored_img = self._restorer.enhance(
                img,
                has_aligned=False,
                only_center_face=False,
                paste_back=True
            )

            # Save
            cv2.imwrite(str(output_path), restored_img)

            # Metadata (Mock for now as GFPGAN doesn't give attributes directly)
            attrs = RestorationAttributes(
                damage_type="restored",
                damage_extent=0.0,
                age=30, # Placeholder
                gender="unknown",
                ethnicity="unknown",
                skin_tone="unknown",
                hair_color="unknown",
                eye_color="unknown",
                tattoo_markers=[],
            )
            return output_path, attrs
            
        except Exception as e:
            print(f"Restoration failed: {e}")
            output_path.write_bytes(image_path.read_bytes())
            return output_path, RestorationAttributes()

