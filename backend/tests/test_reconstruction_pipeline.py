import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.ml.reconstruction.reconstructor import Reconstructor
from app.core.config import settings
import cv2


def test_reconstructor_on_demo_image(tmp_path):
    sample = Path('backend/datasets/demo_faces/picsum_0017.jpg')
    assert sample.exists(), "Sample demo image missing"
    img = cv2.imread(str(sample), cv2.IMREAD_COLOR)
    recon = Reconstructor()
    out_img, conf = recon.reconstruct(img)
    assert out_img is not None
    assert isinstance(conf, float)
    assert out_img.shape[0] > 0 and out_img.shape[1] > 0
    assert conf >= 0.0 and conf <= 1.0


def test_encoder_integration_fallback(tmp_path):
    # Ensure that when no encoder model exists, reconstruct still returns an image
    sample = Path('backend/datasets/demo_faces/picsum_0017.jpg')
    assert sample.exists(), "Sample demo image missing"
    img = cv2.imread(str(sample), cv2.IMREAD_COLOR)
    recon = Reconstructor()
    # force encoder attribute to None to simulate missing encoder
    try:
        recon._encoder = None
    except Exception:
        pass
    out_img, conf = recon.reconstruct(img)
    assert out_img is not None
    assert isinstance(conf, float)
    assert out_img.shape[0] > 0 and out_img.shape[1] > 0
