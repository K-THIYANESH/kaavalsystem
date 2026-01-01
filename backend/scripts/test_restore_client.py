"""Test image restore endpoint using TestClient and a sample image.
"""
import os
import sys

root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, root)
backend_path = os.path.join(root, "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from fastapi.testclient import TestClient

try:
    from app.main import app
except Exception as e:
    raise ImportError(f"Failed to import app.main — sys.path={sys.path}: {e}")


def main():
    client = TestClient(app)
    sample = os.path.join(root, "backend", "datasets", "sample_faces", "sample_face_1.jpg")
    if not os.path.exists(sample):
        print("Sample image not found:", sample)
        return

    with open(sample, "rb") as fh:
        files = {"image_file": ("sample_face_1.jpg", fh, "image/jpeg")}
        r = client.post("/api/image/restore", files=files, timeout=120)
        print("POST /api/image/restore ->", r.status_code)
        try:
            print(r.json())
        except Exception:
            print(r.text)


if __name__ == "__main__":
    main()
