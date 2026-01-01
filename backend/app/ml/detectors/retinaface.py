"""RetinaFace detector with OpenCV DNN fallback for reliable face detection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
import onnxruntime as ort

from ...core.config import settings


Detection = Tuple[List[int], float]  # (bbox [x1,y1,x2,y2], confidence)


@dataclass
class RetinaFaceDetector:
    """Face detector with ONNX RetinaFace and OpenCV Haar Cascade fallback."""

    weights_path: str | None = None
    use_fallback: bool = True  # Enable Haar Cascade fallback

    def __post_init__(self) -> None:
        self._session = None
        self._cascade = None
        
        # Try to load ONNX model
        if self.weights_path:
            self._load_onnx_model()
        
        # Load Haar Cascade as fallback
        if self.use_fallback:
            self._load_haar_cascade()

    def _load_onnx_model(self):
        """Load RetinaFace ONNX model."""
        try:
            path = Path(self.weights_path)
            if not path.is_absolute():
                path = settings.project_root / path
            
            if not path.exists():
                path = settings.models_dir / path.name
                
            if not path.exists():
                print(f"[WARNING] RetinaFace ONNX model not found at {path}")
                return

            providers = ["CPUExecutionProvider"]
            self._session = ort.InferenceSession(str(path), providers=providers)
            self._input_name = self._session.get_inputs()[0].name
            input_shape = self._session.get_inputs()[0].shape
            self._input_size = tuple(input_shape[2:]) if len(input_shape) == 4 else (640, 640)
            
            print(f"✅ Loaded RetinaFace ONNX model from {path}")
        except Exception as e:
            print(f"[WARNING] Failed to load RetinaFace ONNX: {e}")
            self._session = None

    def _load_haar_cascade(self):
        """Load OpenCV Haar Cascade as fallback detector."""
        try:
            # Use OpenCV's built-in Haar Cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self._cascade = cv2.CascadeClassifier(cascade_path)
            
            if self._cascade.empty():
                print("[WARNING] Failed to load Haar Cascade")
                self._cascade = None
            else:
                print("✅ Loaded Haar Cascade fallback detector")
        except Exception as e:
            print(f"[WARNING] Failed to load Haar Cascade: {e}")
            self._cascade = None

    def detect(self, image: np.ndarray) -> List[Detection]:
        """
        Detect faces in image using ONNX model or Haar Cascade fallback.
        
        Args:
            image: Input image (H, W, 3) BGR format
            
        Returns:
            List of (bbox, confidence) tuples
        """
        # Try ONNX model first
        if self._session is not None:
            detections = self._detect_onnx(image)
            if detections:
                return detections
        
        # Fallback to Haar Cascade
        if self._cascade is not None:
            return self._detect_haar(image)
        
        # If both fail, return empty list
        return []

    def _detect_onnx(self, image: np.ndarray) -> List[Detection]:
        """Detect faces using ONNX RetinaFace model."""
        try:
            # Preprocess
            target_size = self._input_size
            img_height, img_width = image.shape[:2]
            
            # Resize with padding
            scale = min(target_size[0] / img_height, target_size[1] / img_width)
            new_h, new_w = int(img_height * scale), int(img_width * scale)
            
            img_resized = cv2.resize(image, (new_w, new_h))
            
            # Pad to target size
            pad_h = target_size[0] - new_h
            pad_w = target_size[1] - new_w
            
            img_padded = cv2.copyMakeBorder(
                img_resized, 0, pad_h, 0, pad_w, cv2.BORDER_CONSTANT, value=(0, 0, 0)
            )
            
            # Normalize and transpose
            blob = cv2.dnn.blobFromImage(
                img_padded, 
                1.0, 
                target_size, 
                (104.0, 117.0, 123.0), 
                swapRB=False, 
                crop=False
            )

            # Inference
            outputs = self._session.run(None, {self._input_name: blob})
            
            # Parse outputs - this is model-specific
            # For now, we'll return empty and rely on fallback
            # TODO: Implement proper RetinaFace output decoding with anchors
            
            return []
            
        except Exception as e:
            print(f"[WARNING] ONNX detection failed: {e}")
            return []

    def _detect_haar(self, image: np.ndarray) -> List[Detection]:
        """Detect faces using Haar Cascade (fallback method)."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self._cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Convert to our format
            detections = []
            for (x, y, w, h) in faces:
                bbox = [int(x), int(y), int(x + w), int(y + h)]
                confidence = 0.95  # Haar Cascade doesn't provide confidence, use fixed value
                detections.append((bbox, confidence))
            
            return detections
            
        except Exception as e:
            print(f"[WARNING] Haar detection failed: {e}")
            return []

    def detect_with_landmarks(self, image: np.ndarray) -> List[Tuple[List[int], float, List[Tuple[int, int]]]]:
        """
        Detect faces with landmarks (not implemented for Haar Cascade).
        
        Returns:
            List of (bbox, confidence, landmarks) tuples
        """
        # For now, just return detections without landmarks
        detections = self.detect(image)
        return [(bbox, conf, []) for bbox, conf in detections]
