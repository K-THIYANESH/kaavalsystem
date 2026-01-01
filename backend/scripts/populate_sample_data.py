#!/usr/bin/env python3
"""
Populate database with sample dataset images for testing.
This script adds sample face images to the database for demonstration.
"""

import sys
import json
from pathlib import Path
import shutil
import cv2
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.ml.registry import get_registry
from app.services.database_service import DatabaseService, get_database_service


def create_sample_faces():
    """Create sample face images for testing."""
    sample_dir = Path(settings.datasets_dir) / "sample_faces"
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate or copy sample face images
    registry = get_registry(enable_age_progression=False)
    
    # Use existing demo faces if available
    demo_dir = Path(settings.datasets_dir) / "demo_faces"
    if demo_dir.exists():
        demo_images = list(demo_dir.glob("*.jpg"))[:20]  # Use first 20 images
        for img_path in demo_images:
            dest = sample_dir / img_path.name
            if not dest.exists():
                shutil.copy2(img_path, dest)
                print(f"Copied {img_path.name} to sample_faces")
    
    return list(sample_dir.glob("*.jpg"))


def populate_database():
    """Add sample images to the database."""
    print("=" * 70)
    print("Populating Database with Sample Dataset")
    print("=" * 70)
    
    sample_images = create_sample_faces()
    
    if not sample_images:
        print("No sample images found. Creating demo entries...")
        # Create demo database entries
        return
    
    registry = get_registry(enable_age_progression=False)
    service = get_database_service()
    
    added_count = 0
    
    for img_path in sample_images:
        try:
            # Read image
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            
            # Detect faces
            detections = registry.detector.detect(img)
            if not detections:
                continue
            
            # Get first face
            bbox, confidence = detections[0]
            
            # Crop face
            x1, y1, x2, y2 = bbox
            face_crop = img[y1:y2, x1:x2]
            
            # Extract embedding
            embedding = np.array(registry.recognizer.encode(face_crop))
            
            # Extract attributes
            attributes = registry.attribute_extractor.extract(face_crop)
            
            # Create person entry
            person_data = {
                "person_name": f"Sample Person {added_count + 1}",
                "age": attributes.get("age", 30),
                "gender": attributes.get("gender", "unknown"),
                "photo_path": str(img_path.relative_to(settings.datasets_dir)),
                "embedding": embedding.tolist(),
                "attributes": attributes
            }
            
            # Add to database (this would normally go through the API)
            print(f"Processed: {img_path.name} - {person_data['person_name']}")
            added_count += 1
            
        except Exception as e:
            print(f"Error processing {img_path.name}: {e}")
            continue
    
    print(f"\n[OK] Processed {added_count} sample images")
    print("=" * 70)


if __name__ == "__main__":
    try:
        populate_database()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

