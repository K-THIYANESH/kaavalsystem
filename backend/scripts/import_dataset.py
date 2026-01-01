"""Bulk import script for adding person images to the KAAVAL database."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import db_session
from app.models.person import Person
from app.models.embedding import Embedding
from app.ml import get_registry
import cv2
import numpy as np


def import_person_images(dataset_dir: str, person_name_prefix: str = "Person") -> None:
    """Import all images from a directory into the database.
    
    Args:
        dataset_dir: Path to directory containing images
        person_name_prefix: Prefix for person names (default: "Person")
    """
    registry = get_registry()
    dataset_path = Path(dataset_dir)
    
    if not dataset_path.exists():
        print(f"Error: Directory {dataset_dir} does not exist")
        return
    
    image_files = list(dataset_path.glob("*.jpg")) + list(dataset_path.glob("*.png")) + list(dataset_path.glob("*.jpeg"))
    
    if not image_files:
        print(f"No image files found in {dataset_dir}")
        return
    
    print(f"Found {len(image_files)} images. Starting import...")
    
    imported = 0
    failed = 0
    
    with db_session() as session:
        for idx, image_file in enumerate(image_files, 1):
            try:
                # Load image
                img = cv2.imread(str(image_file))
                if img is None:
                    print(f"  [{idx}/{len(image_files)}] Failed to load {image_file.name}")
                    failed += 1
                    continue
                
                # Detect face
                faces = registry.detector.detect(img)
                if not faces:
                    print(f"  [{idx}/{len(image_files)}] No face detected in {image_file.name}")
                    failed += 1
                    continue
                
                # Extract embedding from first detected face
                bbox, _ = faces[0]
                from app.ml.utils.image_ops import crop_face
                face_crop = crop_face(img, bbox)
                
                # Extract embedding
                embedding = registry.recognizer.encode(face_crop)
                
                # Extract attributes
                attrs = registry.attribute_extractor.infer(face_crop)
                
                # Create person record
                person = Person(
                    name=f"{person_name_prefix}_{image_file.stem}",
                    age=attrs.get("age"),
                    gender=attrs.get("gender"),
                    ethnicity=attrs.get("ethnicity"),
                    hair_color=attrs.get("hair_color"),
                    eye_color=attrs.get("eye_color"),
                    skin_tone=attrs.get("skin_tone"),
                    photo_path=str(image_file)
                )
                session.add(person)
                session.flush()
                
                # Store embedding
                embedding_obj = Embedding(
                    person_id=person.id,
                    embedding=np.array(embedding, dtype=np.float32).tobytes()
                )
                session.add(embedding_obj)
                
                imported += 1
                print(f"  [{idx}/{len(image_files)}] Imported {image_file.name} (ID: {person.id})")
                
            except Exception as e:
                print(f"  [{idx}/{len(image_files)}] Error processing {image_file.name}: {e}")
                failed += 1
                continue
    
    print(f"\nImport complete: {imported} imported, {failed} failed")
    print("Run 'python -m app.core.init_db' to sync embeddings to FAISS index.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_dataset.py <dataset_directory> [person_name_prefix]")
        print("Example: python import_dataset.py ../datasets/missing_persons MissingPerson")
        sys.exit(1)
    
    dataset_dir = sys.argv[1]
    prefix = sys.argv[2] if len(sys.argv) > 2 else "Person"
    import_person_images(dataset_dir, prefix)

