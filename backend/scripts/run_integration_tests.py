"""Run small in-process integration tests against FastAPI app.

Checks:
- POST /api/database/search with real embedding vector
- POST /api/camera/start and POST /api/camera/stop
- GET /api/results/evidence_pack/example-job

This uses FastAPI TestClient to avoid network flakiness.
"""
import os
import sys
import json

root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, root)
backend_path = os.path.join(root, "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from fastapi.testclient import TestClient
import numpy as np

try:
    from app.main import app
except Exception as e:
    raise ImportError(f"Failed to import app.main — sys.path={sys.path}: {e}")


def load_embedding():
    path = os.path.join(root, "backend", "embeddings_output", "thiyanesh_embeddings.npy")
    if not os.path.exists(path):
        # fallback to any available npy
        folder = os.path.join(root, "backend", "embeddings_output")
        files = [f for f in os.listdir(folder) if f.endswith(".npy")]
        if not files:
            return None
        path = os.path.join(folder, files[0])
    arr = np.load(path)
    # pick first vector
    vec = arr[0].tolist()
    return vec


def main():
    client = TestClient(app)
    print("Running integration tests (in-process)")

    emb = load_embedding()
    if not emb:
        print("No embeddings found; skipping database search test")
    else:
        payload = {
            "embedding_vector": emb,
            "filters": {},
            "return_top_k": 5,
        }
        r = client.post("/api/database/search", json=payload)
        print("POST /api/database/search ->", r.status_code)
        try:
            print(json.dumps(r.json(), indent=2))
        except Exception:
            print(r.text)

    # Camera start/stop
    cam_payload = {"device_id": 0, "frame_skip": 3, "adaptive": True}
    r = client.post("/api/camera/start", json=cam_payload)
    print("POST /api/camera/start ->", r.status_code, r.text)

    r = client.post("/api/camera/stop")
    print("POST /api/camera/stop ->", r.status_code, r.text)

    # Evidence pack
    r = client.get("/api/results/evidence_pack/example-job")
    print("GET /api/results/evidence_pack/example-job ->", r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)


if __name__ == "__main__":
    main()
