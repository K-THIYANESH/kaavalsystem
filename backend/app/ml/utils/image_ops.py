"""Utility helpers for image processing."""

from __future__ import annotations

from typing import Tuple

import cv2  # type: ignore
import numpy as np


def crop_face(image: np.ndarray, bbox: Tuple[int, int, int, int], margin: float = 0.1) -> np.ndarray:
    h, w = image.shape[:2]
    x1, y1, x2, y2 = bbox
    dx = int((x2 - x1) * margin)
    dy = int((y2 - y1) * margin)
    x1 = max(0, x1 - dx)
    y1 = max(0, y1 - dy)
    x2 = min(w, x2 + dx)
    y2 = min(h, y2 + dy)
    return image[y1:y2, x1:x2]


def resize(image: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
    return cv2.resize(image, size)

