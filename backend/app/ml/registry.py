"""Central registry to load and reuse ML components."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from ..core.config import settings
from .detectors.retinaface import RetinaFaceDetector
from .recognizers.arcface import ArcFaceRecognizer
from .attributes.attribute_net import AttributeExtractor
from .restoration.gfpgan import GFPGANRestorer
from .age_progression.stylegan import StyleGANAgeProgressor
import logging
from .matching.coarse_to_fine import CoarseToFineMatcher


@dataclass
class ModelRegistry:
    """Provide singleton instances for heavy models."""

    detector: RetinaFaceDetector
    recognizer: ArcFaceRecognizer
    attribute_extractor: AttributeExtractor
    restorer: GFPGANRestorer
    age_progressor: Optional[StyleGANAgeProgressor]
    matcher: CoarseToFineMatcher


@lru_cache()
def get_registry(enable_age_progression: bool = True) -> ModelRegistry:
    manifest_path = settings.models_dir / "manifest.json"
    manifest = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    detector_weights = manifest.get("detector", {}).get("weights") if manifest else None
    recognizer_weights = manifest.get("recognizer", {}).get("weights") if manifest else None
    attribute_weights = manifest.get("attribute", {}).get("weights") if manifest else None
    restorer_weights = manifest.get("restorer", {}).get("weights") if manifest else None
    age_weights = manifest.get("age_progression", {}).get("weights") if manifest else None

    detector = RetinaFaceDetector(weights_path=detector_weights)
    recognizer = ArcFaceRecognizer(weights_path=recognizer_weights)
    attribute_extractor = AttributeExtractor(weights_path=attribute_weights)
    restorer = GFPGANRestorer(weights_path=restorer_weights)
    matcher = CoarseToFineMatcher()
    age_progressor = None
    if enable_age_progression:
        if age_weights:
            try:
                age_progressor = StyleGANAgeProgressor(weights_path=age_weights)
            except Exception as e:
                logging.getLogger(__name__).warning(
                    'Failed to load StyleGAN age progression model: %s. Age progression disabled. '
                    'To enable, ensure the training/runtime modules used to save the checkpoint (e.g. torch_utils/dnnlib) '
                    'are available or re-export the model as a weights-only state_dict.',
                    e,
                )
        else:
            logging.getLogger(__name__).warning('Age progression enabled but no weights configured in manifest; skipping.')
    return ModelRegistry(
        detector=detector,
        recognizer=recognizer,
        attribute_extractor=attribute_extractor,
        restorer=restorer,
        age_progressor=age_progressor,
        matcher=matcher,
    )

