"""Quality scoring utilities for video frames."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np


@dataclass
class QualityScore:
    total: float
    metrics: Dict[str, float]


def assess_frame(frame: np.ndarray) -> QualityScore:
    laplacian = float(np.var(np.gradient(frame.astype(np.float32))))
    illumination = float(np.mean(frame)) / 255.0
    size_factor = 0.5
    pose = 0.8
    occlusion = 0.1
    total = 0.25 * laplacian + 0.25 * illumination + 0.25 * size_factor + 0.15 * pose + 0.1 * (1 - occlusion)
    return QualityScore(
        total=total,
        metrics={
            "sharpness": laplacian,
            "illumination": illumination,
            "size": size_factor,
            "pose": pose,
            "occlusion": occlusion,
        },
    )

