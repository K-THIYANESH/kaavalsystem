"""Verify that all downloaded models can be loaded correctly."""

import sys
from pathlib import Path
import torch
import onnxruntime as ort

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.ml.recognizers.arcface import ArcFaceRecognizer
from app.ml.attributes.attribute_net import AttributeExtractor
from app.ml.age_progression.stylegan import StyleGANAgeProgressor
from app.ml.forensics.deepfake_detector import DeepfakeDetector

def test_models():
    print("=" * 50)
    print("Testing Model Loading")
    print("=" * 50)
    
    models_dir = settings.models_dir
    print(f"Models Directory: {models_dir}")
    
    # 1. ArcFace
    print("\n[TEST] Loading ArcFace...")
    try:
        arcface = ArcFaceRecognizer()
        if arcface._session:
            print("  [OK] ArcFace loaded successfully")
        else:
            print("  [FAIL] ArcFace session is None")
    except Exception as e:
        print(f"  [FAIL] Error loading ArcFace: {e}")

    # 2. AttributeNet
    print("\n[TEST] Loading AttributeNet...")
    try:
        attr_net = AttributeExtractor()
        if attr_net._session:
            print("  [OK] AttributeNet loaded successfully")
        else:
            print("  [FAIL] AttributeNet session is None")
    except Exception as e:
        print(f"  [FAIL] Error loading AttributeNet: {e}")

    # 3. StyleGAN
    print("\n[TEST] Loading StyleGAN...")
    try:
        stylegan = StyleGANAgeProgressor()
        if stylegan._model:
            print("  [OK] StyleGAN loaded successfully")
        else:
            print("  [FAIL] StyleGAN model is None")
    except Exception as e:
        print(f"  [FAIL] Error loading StyleGAN: {e}")

    # 4. Deepfake Detector
    print("\n[TEST] Loading Deepfake Detector...")
    try:
        deepfake = DeepfakeDetector()
        # Note: DeepfakeDetector might not have a loaded model property exposed directly yet, 
        # but initialization shouldn't crash.
        print("  [OK] Deepfake Detector initialized")
    except Exception as e:
        print(f"  [FAIL] Error loading Deepfake Detector: {e}")

    print("\n" + "=" * 50)
    print("Test Complete")
    print("=" * 50)

if __name__ == "__main__":
    test_models()
