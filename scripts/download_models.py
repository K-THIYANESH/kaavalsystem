"""Download required model artifacts listed in `scripts/models_manifest.json`.

Usage:
  python scripts/download_models.py [--manifest path] [--models-dir path]

If a model entry has an empty URL, it will be skipped and reported.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Optional

import requests


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path) -> None:
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def main(manifest: Optional[Path] = None, models_dir: Optional[Path] = None) -> None:
    manifest = manifest or Path(__file__).with_name("models_manifest.json")
    models_dir = models_dir or Path(__file__).resolve().parents[1] / "backend" / "models"

    print("Manifest:", manifest)
    print("Models dir:", models_dir)

    data = json.loads(manifest.read_text(encoding="utf-8"))
    for entry in data.get("models", []):
        name = entry.get("name")
        url = entry.get("url")
        checksum = entry.get("sha256") or entry.get("sha") or ""
        dest = models_dir / name

        if dest.exists():
            print(f"Exists: {name} ({dest.stat().st_size} bytes)")
            if checksum:
                local_sha = sha256_of_file(dest)
                if local_sha.lower() == checksum.lower():
                    print("  checksum OK")
                    continue
                else:
                    print("  checksum mismatch; re-downloading")
        if not url:
            print(f"Skipping {name}: no URL provided in manifest")
            continue
        print(f"Downloading {name} from {url} -> {dest}")
        try:
            download(url, dest)
        except Exception as e:
            print(f"Failed to download {name}: {e}")
            continue
        if checksum:
            local_sha = sha256_of_file(dest)
            if local_sha.lower() != checksum.lower():
                print(f"Warning: checksum mismatch for {name}")


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--manifest", default=None)
    p.add_argument("--models-dir", default=None)
    args = p.parse_args()

    manifest_path = Path(args.manifest) if args.manifest else None
    models_dir_path = Path(args.models_dir) if args.models_dir else None
    main(manifest_path, models_dir_path)
