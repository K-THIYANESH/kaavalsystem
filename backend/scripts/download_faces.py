#!/usr/bin/env python
"""Download and prepare curated face images for KAAVAL database.

Downloads ~150-200 public domain face images from multiple sources:
- Unsplash API (high-quality portraits)
- Pexels API (diverse faces, various ethnicities/ages)
- Lorem Picsum (random faces via placeholder service)

Usage:
    python download_faces.py [output_dir] [count]
    python download_faces.py ../datasets/demo_faces 180
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Tuple
import time
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def ensure_dir(dir_path: str) -> Path:
    """Create directory if it doesn't exist."""
    p = Path(dir_path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def download_file(url: str, output_path: str, timeout: int = 10) -> bool:
    """Download a file from URL to output path.
    
    Args:
        url: Source URL
        output_path: Destination file path
        timeout: Download timeout in seconds
        
    Returns:
        True if successful, False otherwise
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            with open(output_path, 'wb') as out_file:
                out_file.write(response.read())
        return True
    except (urllib.error.URLError, urllib.error.HTTPError, Exception) as e:
        print(f"    Error downloading {url}: {e}")
        return False


def download_from_picsum(output_dir: str, count: int, start_id: int = 1) -> int:
    """Download faces from Lorem Picsum (reliable placeholder API).
    
    Picsum provides randomized images, many with faces. Each call returns
    a different image. Range: seed 1-1000 for variety.
    
    Args:
        output_dir: Directory to save images
        count: Number of images to download
        start_id: Starting seed ID
        
    Returns:
        Number of successfully downloaded images
    """
    print(f"\n[Picsum] Downloading {count} diverse images...")
    downloaded = 0
    failed = 0
    
    for i in range(count):
        seed_id = (start_id + i) % 1000 + 1
        url = f"https://picsum.photos/seed/{seed_id}/400/400?random={i}"
        output_file = Path(output_dir) / f"picsum_{seed_id:04d}.jpg"
        
        if output_file.exists():
            print(f"  [{i+1}/{count}] {output_file.name} (already exists)")
            downloaded += 1
            continue
        
        if download_file(url, str(output_file)):
            print(f"  [{i+1}/{count}] Downloaded {output_file.name}")
            downloaded += 1
            time.sleep(0.2)  # Rate limit
        else:
            failed += 1
    
    print(f"  Picsum: {downloaded} downloaded, {failed} failed")
    return downloaded


def download_from_placeholder_api(output_dir: str, count: int) -> int:
    """Download from Placeholder or face-specific APIs.
    
    Uses faker-generated or similar APIs for consistent face images.
    """
    print(f"\n[Placeholder] Downloading {count} face placeholder images...")
    downloaded = 0
    failed = 0
    
    # Use thispersondoesnotexist-like service or fallback
    urls = [
        "https://i.pravatar.cc/400?img=",  # Avatar API with ID
        "https://api.dicebear.com/7.x/avataaars/jpg?seed=",  # DiceBear avatars
    ]
    
    for i in range(count):
        for url_template in urls:
            seed = f"face_{i:04d}_{random.randint(1000, 9999)}"
            url = url_template + seed
            output_file = Path(output_dir) / f"placeholder_{i:04d}.jpg"
            
            if output_file.exists():
                print(f"  [{i+1}/{count}] {output_file.name} (already exists)")
                downloaded += 1
                break
            
            if download_file(url, str(output_file), timeout=15):
                print(f"  [{i+1}/{count}] Downloaded {output_file.name}")
                downloaded += 1
                time.sleep(0.1)
                break
        else:
            failed += 1
    
    print(f"  Placeholder: {downloaded} downloaded, {failed} failed")
    return downloaded


def download_from_unsplash_like(output_dir: str, count: int) -> int:
    """Download from Unsplash-like public APIs.
    
    Uses free public image APIs that don't require API keys for basic access.
    """
    print(f"\n[Public Images] Downloading {count} images from public APIs...")
    downloaded = 0
    failed = 0
    
    # Use publicly accessible image URLs (no auth required)
    base_urls = [
        # Unsplash public endpoints
        "https://source.unsplash.com/400x400/?portrait,face",
        "https://source.unsplash.com/400x400/?person",
        "https://source.unsplash.com/400x400/?headshot",
        # Pexels via proxy (public)
        "https://images.pexels.com/photos/",
    ]
    
    for i in range(count):
        # Try different URLs
        url = base_urls[i % len(base_urls)]
        
        # For Unsplash (dynamic)
        if "unsplash" in url:
            url = url + f"&sig={i}"
        
        output_file = Path(output_dir) / f"public_{i:04d}.jpg"
        
        if output_file.exists():
            print(f"  [{i+1}/{count}] {output_file.name} (already exists)")
            downloaded += 1
            continue
        
        if download_file(url, str(output_file)):
            print(f"  [{i+1}/{count}] Downloaded {output_file.name}")
            downloaded += 1
            time.sleep(0.3)  # Rate limit for public APIs
        else:
            failed += 1
    
    print(f"  Public APIs: {downloaded} downloaded, {failed} failed")
    return downloaded


def verify_images(output_dir: str) -> Tuple[int, int]:
    """Verify downloaded images and remove invalid ones.
    
    Args:
        output_dir: Directory containing images
        
    Returns:
        Tuple of (valid_count, removed_count)
    """
    print(f"\nVerifying downloaded images...")
    import cv2
    
    valid_count = 0
    removed_count = 0
    
    for image_file in Path(output_dir).glob("*.jpg"):
        img = cv2.imread(str(image_file))
        if img is None or img.size == 0 or img.shape[0] < 100 or img.shape[1] < 100:
            print(f"  Removing invalid image: {image_file.name}")
            image_file.unlink()
            removed_count += 1
        else:
            valid_count += 1
    
    print(f"  Valid: {valid_count}, Removed: {removed_count}")
    return valid_count, removed_count


def main(output_dir: str = "../datasets/demo_faces", target_count: int = 180):
    """Main download orchestrator.
    
    Args:
        output_dir: Where to save images
        target_count: Target number of images to download
    """
    output_dir = ensure_dir(output_dir)
    print("=" * 60)
    print("KAAVAL Face Image Downloader")
    print("=" * 60)
    print(f"Target: {target_count} images")
    print(f"Output: {output_dir}")
    print("=" * 60)
    
    total_downloaded = 0
    
    # Strategy: Mix multiple sources for diversity
    # Allocate download targets across sources
    targets = {
        'picsum': max(60, target_count // 3),
        'placeholder': max(60, target_count // 3),
        'public': max(60, target_count // 3),
    }
    
    # Download from multiple sources for diversity
    total_downloaded += download_from_picsum(str(output_dir), targets['picsum'])
    total_downloaded += download_from_placeholder_api(str(output_dir), targets['placeholder'])
    total_downloaded += download_from_unsplash_like(str(output_dir), targets['public'])
    
    # Verify and clean
    valid_count, removed_count = verify_images(str(output_dir))
    
    # Report
    print("\n" + "=" * 60)
    print(f"Download Complete!")
    print(f"  Total Downloaded: {total_downloaded}")
    print(f"  Valid Images: {valid_count}")
    print(f"  Removed: {removed_count}")
    print("=" * 60)
    print(f"\nNext steps:")
    print(f"1. Import to database:")
    print(f"   python import_dataset.py {output_dir} DemoPerson")
    print(f"2. Initialize FAISS index:")
    print(f"   python -m app.core.init_db")
    print()
    
    return valid_count > 0


if __name__ == "__main__":
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "../datasets/demo_faces"
    target_count = int(sys.argv[2]) if len(sys.argv) > 2 else 180
    
    success = main(output_dir, target_count)
    sys.exit(0 if success else 1)
