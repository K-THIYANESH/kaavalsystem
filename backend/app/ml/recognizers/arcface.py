"""ArcFace embedding extractor using ONNX Runtime."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import cv2
import numpy as np
import onnxruntime as ort

from ...core.config import settings


@dataclass
class ArcFaceRecognizer:
    """Generate 512-d embeddings via ArcFace."""

    weights_path: str | None = None

    def __post_init__(self) -> None:
        self._session = None
        if not self.weights_path:
            return

        path = Path(self.weights_path)
        if not path.is_absolute():
            path = settings.project_root / path
            
        if not path.exists():
            path = settings.models_dir / path.name
            
        if not path.exists():
            print(f"WARNING: ArcFace model not found at {path}")
            self._session = None
            return

        providers = ["CPUExecutionProvider"]
        try:
            self._session = ort.InferenceSession(str(path), providers=providers)
            print(f"✅ Loaded ArcFace model from {path}")
        except Exception as e:
            print(f"Error loading ArcFace model: {e}")
            self._session = None
            return
            
        self._input_name = self._session.get_inputs()[0].name
        self.embedding_size = 512

    def encode(self, face_image: np.ndarray) -> List[float]:
        """Return 512-d embedding for the cropped face."""
        if self._session is None:
            return [0.0] * 512

        # Preprocess: Resize to 112x112, normalize
        img = cv2.resize(face_image, (112, 112))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = np.transpose(img, (2, 0, 1))
        img = np.expand_dims(img, axis=0)
        img = (img - 127.5) / 128.0
        img = img.astype(np.float32)

        # Inference
        try:
            outputs = self._session.run(None, {self._input_name: img})
            embedding = outputs[0][0]
            
            # Normalize
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
                
            return embedding.tolist()
        except Exception as e:
            print(f"ArcFace inference error: {e}")
            return [0.0] * 512

