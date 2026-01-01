"""Attribute extraction using ONNX Runtime."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import cv2
import numpy as np
import onnxruntime as ort

from ...core.config import settings


@dataclass
class AttributeExtractor:
    """Return soft attribute predictions for a face crop."""

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
            print(f"WARNING: AttributeNet model not found at {path}")
            return

        providers = ["CPUExecutionProvider"]
        try:
            self._session = ort.InferenceSession(str(path), providers=providers)
            self._input_name = self._session.get_inputs()[0].name
            print(f"✅ Loaded AttributeNet model from {path}")
        except Exception as e:
            print(f"Error loading AttributeNet model: {e}")
            self._session = None

    def infer(self, face_image: np.ndarray) -> Dict[str, float | str]:
        """Extract attributes from a face crop."""
        if self._session is None:
            return self._get_mock_attributes()

        try:
            # Preprocess: Resize to 224x224
            img = cv2.resize(face_image, (224, 224))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = np.transpose(img, (2, 0, 1))
            img = np.expand_dims(img, axis=0)
            img = (img - 127.5) / 128.0
            img = img.astype(np.float32)

            # Run inference
            outputs = self._session.run(None, {self._input_name: img})
            
            # Defensive check: if outputs structure doesn't match expected, return mock
            if not outputs or len(outputs) == 0:
                return self._get_mock_attributes()
            
            attributes = {}
            
            # Try to parse outputs with defensive checks
            try:
                if len(outputs) >= 2 and len(outputs[0]) > 0 and len(outputs[1]) > 0:
                    # Gender
                    gender_scores = outputs[1][0]
                    gender_idx = np.argmax(gender_scores)
                    attributes["gender"] = "Male" if gender_idx == 0 else "Female"
                    
                    # Race/Ethnicity
                    race_scores = outputs[0][0]
                    races = ["White", "Black", "Latino_Hispanic", "East_Asian", "Southeast_Asian", "Indian", "Middle_Eastern"]
                    if len(race_scores) == len(races):
                        attributes["ethnicity"] = races[np.argmax(race_scores)]
                    else:
                        attributes["ethnicity"] = "Unknown"

                if len(outputs) >= 3 and len(outputs[2]) > 0:
                    # Age
                    age_scores = outputs[2][0]
                    age_ranges = [1, 6, 15, 25, 35, 45, 55, 65, 75]
                    predicted_age_idx = np.argmax(age_scores)
                    attributes["age"] = age_ranges[predicted_age_idx] if predicted_age_idx < len(age_ranges) else 30
            except (IndexError, KeyError, ValueError):
                # If parsing fails, fall back to mock
                pass
            
            # Fallback for missing heads or single-vector models
            if not attributes:
                 return self._get_mock_attributes()

            # Add placeholders for other attributes not yet in model
            attributes.setdefault("hair_color", "Unknown")
            attributes.setdefault("eye_color", "Unknown")
            attributes.setdefault("skin_tone", "Unknown")
            attributes.setdefault("age", 30)
            attributes.setdefault("gender", "Unknown")
            attributes.setdefault("ethnicity", "Unknown")
            
            return attributes
            
        except Exception as e:
            print(f"Attribute inference error: {e}")
            return self._get_mock_attributes()

    def _get_mock_attributes(self) -> Dict[str, float | str]:
        return {
            "age": 28,
            "gender": "Female",
            "ethnicity": "South Asian",
            "skin_tone": "Warm",
            "hair_color": "Black",
            "eye_color": "Brown",
            "tattoo": 0.0,
            "scar": 0.0,
        }
