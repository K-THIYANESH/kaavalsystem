#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Download all required pretrained models for KAAVAL facial recognition system.
Downloads models from reliable sources and places them in the correct format.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from urllib.request import urlretrieve, urlopen
from urllib.error import URLError, HTTPError
import zipfile
import tempfile

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Model URLs - Using reliable direct download sources
MODEL_URLS = {
    "deepfake_detector.pth": {
        "urls": [
            "http://data.lip6.fr/cadene/pretrainedmodels/xception-43020ad28.pth",
            "https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-cadene/xception-43020ad28.pth"
        ],
        "size_mb": 88,
        "description": "Xception model for Deepfake Detection"
    },
    "retinaface.onnx": {
        "urls": [
            "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip",
        ],
        "extract_from_zip": "buffalo_l/models/det_10g.onnx",
        "size_mb": 19,
        "description": "RetinaFace face detector"
    },
    "arcface_resnet100.onnx": {
        "urls": [
            "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip",
        ],
        "extract_from_zip": "buffalo_l/models/w600k_r50.onnx",
        "size_mb": 248,
        "description": "ArcFace face recognition"
    },
    "attribute_net.onnx": {
        "urls": [
            "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip",
        ],
        "extract_from_zip": "buffalo_l/models/genderage.onnx",
        "size_mb": 1.1,
        "description": "Age/Gender attribute detector"
    },
    "gfpgan.pth": {
        "urls": [
            "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth",
        ],
        "size_mb": 332,
        "description": "GFPGAN face restoration"
    },
    "stylegan2_age.pt": {
        "urls": [
            "https://nvlabs-fi-cdn.nvidia.com/stylegan2-ada-pytorch/pretrained/ffhq.pkl",
        ],
        "size_mb": 363,
        "description": "StyleGAN2 (FFHQ) for age progression",
        "optional": True
    }
    ,
    "psp_encoder.pth": {
        "urls": [
            "https://huggingface.co/trysem/pixel2style2pixel/resolve/main/psp_ffhq_encode.pt"
        ],
        "size_mb": 1200,
        "description": "pSp encoder (FFHQ) for latent inversion",
        "optional": True
    }
}

# Sample dataset images for testing
DATASET_IMAGES = [
    {
        "url": "https://raw.githubusercontent.com/deepinsight/insightface/master/python-package/insightface/data/images/Tom_Hanks_54745.png",
        "filename": "sample_face_1.jpg"
    },
    {
        "url": "https://raw.githubusercontent.com/deepinsight/insightface/master/python-package/insightface/data/images/Tom_Cruise_54746.png",
        "filename": "sample_face_2.jpg"
    },
]


def format_size(size_bytes):
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def get_file_size(url):
    """Get file size from URL."""
    try:
        response = urlopen(url)
        size = int(response.headers.get('Content-Length', 0))
        response.close()
        return size
    except:
        return 0


def download_file(url: str, dest_path: Path, description: str = ""):
    """Download a file with progress indication."""
    print(f"  Downloading from: {url[:160]}...")
    # Download to temporary .part file and rename on success to avoid corrupt files
    part_path = dest_path.with_suffix(dest_path.suffix + '.part')
    attempts = 3
    for attempt in range(1, attempts + 1):
        try:
            file_size = get_file_size(url)
            downloaded = 0

            def reporthook(count, block_size, total_size):
                nonlocal downloaded
                downloaded = count * block_size
                if total_size > 0:
                    percent = min(100, (downloaded * 100) // total_size)
                    print(f"\r    Progress: {percent}% ({format_size(downloaded)}/{format_size(total_size)})", end='', flush=True)
                else:
                    print(f"\r    Downloaded: {format_size(downloaded)}", end='', flush=True)

            # Ensure partial file removed before starting
            if part_path.exists():
                try:
                    part_path.unlink()
                except Exception:
                    pass

            urlretrieve(url, part_path, reporthook=reporthook)
            print("\n    [OK] Download complete!")

            if part_path.exists():
                # Move/rename atomically
                try:
                    if dest_path.exists():
                        dest_path.unlink()
                    part_path.rename(dest_path)
                except Exception:
                    # Fallback to copy
                    shutil.copy2(part_path, dest_path)
                    part_path.unlink()

                actual_size = dest_path.stat().st_size
                print(f"    File size: {format_size(actual_size)}")
                return True
            return False

        except HTTPError as e:
            print(f"\n    [ERROR] HTTP Error {e.code}: {e.reason}")
            # retry on server errors
        except URLError as e:
            print(f"\n    [ERROR] URL Error: {e.reason}")
            # retry on network errors
        except Exception as e:
            print(f"\n    [ERROR] Error: {e}")

        if attempt < attempts:
            print(f"    [INFO] Retrying ({attempt}/{attempts})...")
        else:
            print("    [ERROR] Exhausted retries")
    return False


def extract_from_zip(zip_path: Path, extract_to: Path, target_file: str):
    """Extract specific file from zip archive."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Check if file exists in zip
            if target_file not in zip_ref.namelist():
                # Try to find similar file
                for name in zip_ref.namelist():
                    if 'retinaface' in name.lower() and name.endswith('.onnx'):
                        target_file = name
                        break
                    elif 'arcface' in name.lower() and name.endswith('.onnx'):
                        target_file = name
                        break
                    elif 'genderage' in name.lower() and name.endswith('.onnx'):
                        target_file = name
                        break
            
            if target_file in zip_ref.namelist():
                zip_ref.extract(target_file, extract_to)
                extracted_path = extract_to / target_file
                if extracted_path.exists():
                    return extracted_path
        return None
    except Exception as e:
        print(f"    [ERROR] Extraction failed: {e}")
        return None


def download_model(model_name: str, model_info: dict, models_dir: Path):
    """Download a single model with fallback URLs."""
    dest_path = models_dir / model_name
    
    # Check if already exists
    # Check if already exists and verify size
    if dest_path.exists():
        size_mb = dest_path.stat().st_size / (1024 * 1024)
        expected_mb = model_info.get("size_mb", 0)
        
        # Allow 10% tolerance or if size is unknown
        if expected_mb == 0 or abs(size_mb - expected_mb) / expected_mb < 0.1:
            print(f"[OK] {model_name} already exists ({size_mb:.2f} MB)")
            return True
        else:
            print(f"[WARNING] {model_name} size mismatch (Found: {size_mb:.2f} MB, Expected: ~{expected_mb} MB). Re-downloading...")
            dest_path.unlink()
    
    print(f"\n[DOWNLOAD] {model_info['description']} ({model_info.get('size_mb', '?')} MB)")
    
    # Try each URL
    for url in model_info["urls"]:
        if model_info.get("extract_from_zip"):
            # Download zip and extract
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                tmp_zip = Path(tmp_file.name)
            
            try:
                if download_file(url, tmp_zip, model_info["description"]):
                    extracted = extract_from_zip(tmp_zip, models_dir, model_info["extract_from_zip"])
                    if extracted and extracted.exists():
                        # Move to final location
                        if extracted != dest_path:
                            if dest_path.exists():
                                dest_path.unlink()
                            extracted.rename(dest_path)
                        print(f"  [OK] {model_name} extracted successfully")
                        tmp_zip.unlink()
                        return True
                tmp_zip.unlink()
            except Exception as e:
                if tmp_zip.exists():
                    tmp_zip.unlink()
                print(f"  [ERROR] Failed: {e}")
        else:
            # Direct download
            if download_file(url, dest_path, model_info["description"]):
                if dest_path.exists():
                    print(f"  [OK] {model_name} downloaded successfully")
                    # Compute checksum for the downloaded file
                    try:
                        import hashlib
                        h = hashlib.sha256()
                        with open(dest_path, 'rb') as fh:
                            for chunk in iter(lambda: fh.read(8192), b''):
                                h.update(chunk)
                        sha256 = h.hexdigest()
                        # Save checksum next to file
                        checksum_path = dest_path.with_suffix(dest_path.suffix + '.sha256')
                        with open(checksum_path, 'w', encoding='utf-8') as chf:
                            chf.write(sha256)
                        print(f"    [OK] SHA256: {sha256}")
                    except Exception:
                        pass
                    return True
    
    print(f"  [ERROR] Failed to download {model_name} from all sources")
    return False


def download_models(models_dir: Path, skip_optional: bool = False):
    """Download all required models."""
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("KAAVAL Model Downloader")
    print("=" * 70)
    print(f"Models directory: {models_dir}")
    print()
    
    downloaded = []
    skipped = []
    failed = []
    
    for model_name, model_info in MODEL_URLS.items():
        if skip_optional and model_info.get("optional", False):
            print(f"[SKIP] Skipping optional model: {model_name}")
            skipped.append(model_name)
            continue
        
        if download_model(model_name, model_info, models_dir):
            downloaded.append(model_name)
        else:
            failed.append(model_name)

    # After initial pass, verify models and retry any that look corrupted
    def verify_and_fix():
        for model_name, model_info in MODEL_URLS.items():
            if skip_optional and model_info.get("optional", False):
                continue
            model_path = models_dir / model_name
            # If file missing or zero length, attempt re-download
            if not model_path.exists() or model_path.stat().st_size == 0:
                print(f"[VERIFY] {model_name} missing or empty; re-downloading...")
                # remove any partials
                part = model_path.with_suffix(model_path.suffix + '.part')
                if part.exists():
                    try:
                        part.unlink()
                    except Exception:
                        pass
                # Try to download again using same logic
                if download_model(model_name, model_info, models_dir):
                    print(f"  [OK] {model_name} recovered")
                else:
                    print(f"  [ERROR] {model_name} could not be recovered")

    verify_and_fix()
    
    # Handle GFPGAN - check if we have GFPGANv1.4.pth and create copy
    gfpgan_v14 = models_dir / "GFPGANv1.4.pth"
    gfpgan_target = models_dir / "gfpgan.pth"
    if gfpgan_v14.exists() and not gfpgan_target.exists():
        print("\n[INFO] Creating gfpgan.pth from existing GFPGANv1.4.pth...")
        shutil.copy2(gfpgan_v14, gfpgan_target)
        print(f"  [OK] Created {gfpgan_target}")
        if "gfpgan.pth" not in downloaded:
            downloaded.append("gfpgan.pth")
    
    print("\n" + "=" * 70)
    print("Download Summary:")
    print(f"  [OK] Downloaded: {len(downloaded)} - {', '.join(downloaded)}")
    if skipped:
        print(f"  [SKIP] Skipped: {len(skipped)} - {', '.join(skipped)}")
    if failed:
        print(f"  [ERROR] Failed: {len(failed)} - {', '.join(failed)}")
    print("=" * 70)
    
    return downloaded, skipped, failed


def download_dataset_images(dataset_dir: Path):
    """Download sample dataset images for testing."""
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 70)
    print("Downloading Sample Dataset Images")
    print("=" * 70)
    
    downloaded_images = []
    
    for img_info in DATASET_IMAGES:
        dest_path = dataset_dir / img_info["filename"]
        
        if dest_path.exists():
            print(f"[OK] {img_info['filename']} already exists")
            downloaded_images.append(img_info["filename"])
            continue
        
        print(f"\n[DOWNLOAD] Downloading {img_info['filename']}...")
        if download_file(img_info["url"], dest_path, img_info["filename"]):
            downloaded_images.append(img_info["filename"])
    
    print(f"\n[OK] Downloaded {len(downloaded_images)} sample images")
    return downloaded_images


def update_manifest(models_dir: Path):
    """Update manifest.json with downloaded models."""
    manifest_path = models_dir / "manifest.json"
    
    manifest = {
        "detector": {
            "name": "RetinaFace-MobileNet",
            "version": "1.0.0",
            "weights": "models/retinaface.onnx",
            "input_size": [640, 640]
        },
        "recognizer": {
            "name": "ArcFace-ResNet100",
            "version": "1.0.0",
            "weights": "models/arcface_resnet100.onnx",
            "embedding_dim": 512
        },
        "attribute": {
            "name": "KAAVAL-AttributeNet",
            "version": "0.9.1",
            "weights": "models/attribute_net.onnx"
        },
        "restorer": {
            "name": "GFPGANv1.4",
            "weights": "models/gfpgan.pth"
        },
        "age_progression": {
            "name": "StyleGAN2-Age",
            "weights": "models/stylegan2_age.pt"
        }
    }
    
    # Check which models exist and update paths
    # Add checksums where possible
    for key, model_info in manifest.items():
        model_file = model_info.get("weights", "").replace("models/", "")
        model_path = models_dir / model_file
        if not model_path.exists():
            # Try alternative names
            if model_file == "gfpgan.pth":
                alt_path = models_dir / "GFPGANv1.4.pth"
                if alt_path.exists():
                    manifest[key]["weights"] = "models/GFPGANv1.4.pth"
                    model_path = alt_path

        # If the file exists, attempt to read accompanying .sha256 or compute one
        try:
            if model_path.exists():
                checksum_file = model_path.with_suffix(model_path.suffix + '.sha256')
                if checksum_file.exists():
                    with open(checksum_file, 'r', encoding='utf-8') as cf:
                        sha = cf.read().strip()
                else:
                    # compute on the fly
                    import hashlib
                    h = hashlib.sha256()
                    with open(model_path, 'rb') as fh:
                        for chunk in iter(lambda: fh.read(8192), b''):
                            h.update(chunk)
                    sha = h.hexdigest()
                manifest[key]["sha256"] = sha
        except Exception:
            pass
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n[OK] Updated {manifest_path}")


def main():
    """Main download function."""
    project_root = Path(__file__).parent.parent.parent
    models_dir = project_root / "backend" / "models"
    dataset_dir = project_root / "backend" / "datasets" / "sample_faces"
    
    import argparse
    parser = argparse.ArgumentParser(description="Download KAAVAL pretrained models")
    parser.add_argument("--skip-optional", action="store_true", help="Skip optional models")
    parser.add_argument("--skip-images", action="store_true", help="Skip dataset images")
    args = parser.parse_args()
    
    try:
        # Download models
        downloaded, skipped, failed = download_models(models_dir, skip_optional=args.skip_optional)
        
        # Download dataset images
        if not args.skip_images:
            download_dataset_images(dataset_dir)
        
        # Update manifest
        update_manifest(models_dir)
        
        print("\n" + "=" * 70)
        print("[SUCCESS] Model download process completed!")
        print("=" * 70)
        
        if failed:
            print("\n[WARNING] Some models failed to download. You may need to:")
            print("  1. Check your internet connection")
            print("  2. Download manually from HuggingFace or GitHub")
            print("  3. Place them in:", models_dir)
            print("\nRecommended manual download links:")
            print("  - RetinaFace: https://huggingface.co/spaces/deepinsight/antelope")
            print("  - ArcFace: https://huggingface.co/spaces/deepinsight/antelope")
            print("  - GFPGAN: https://github.com/TencentARC/GFPGAN/releases")
        
        return 0 if not failed else 1
        
    except KeyboardInterrupt:
        print("\n\n[WARNING] Download interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
