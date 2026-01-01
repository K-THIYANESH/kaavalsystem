"""In-process smoke tests using FastAPI TestClient.

This avoids network issues by calling the ASGI app directly.
"""
import os
import sys

# Ensure package discovery finds `app` package
root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, root)
# Also ensure `backend` package path is available for direct imports
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
    for path in ["/", "/healthz", "/api/database/stats", "/api/analytics"]:
        r = client.get(path)
        print(f"{path} -> {r.status_code} | {r.text}")


if __name__ == "__main__":
    main()
