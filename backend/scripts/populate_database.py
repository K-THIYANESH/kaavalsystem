"""Update populate_database.py to use new AttributeExtractor and generate embeddings."""

import sys
from pathlib import Path
import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.person import Person
from app.models.embedding import Embedding
from app.ml.recognizers.arcface import ArcFaceRecognizer
from app.ml.attributes.attribute_net import AttributeExtractor
from app.ml.detectors.retinaface import RetinaFaceDetector
from app.core.config import settings

def populate_database():
    """Populate database with sample persons, embeddings, and attributes."""
    
    print("=" * 60)
    print("Populating Database with Sample Data")
    print("=" * 60)
    
    # Initialize ML models
    print("\n[STEP 1] Initializing ML models...")
    detector = RetinaFaceDetector()
    recognizer = ArcFaceRecognizer(weights_path="models/arcface_resnet100.onnx")
    attribute_extractor = AttributeExtractor(weights_path="models/attribute_net.onnx")
    
    # Check if datasets directory exists
    datasets_dir = settings.project_root / "datasets" / "sample_faces"
    if not datasets_dir.exists():
        print(f"\n❌ Datasets directory not found: {datasets_dir}")
        print("Please create the directory and add sample face images.")
        print("Expected structure: datasets/sample_faces/*.jpg")
        return 1
    
    # Get all image files
    image_files = list(datasets_dir.glob("*.jpg")) + list(datasets_dir.glob("*.png"))
    if not image_files:
        print(f"\n❌ No images found in {datasets_dir}")
        return 1
    
    print(f"Found {len(image_files)} images")
    
    # Process each image
    print("\n[STEP 2] Processing images and extracting features...")
    with SessionLocal() as session:
        for idx, image_path in enumerate(image_files, 1):
            print(f"\nProcessing {idx}/{len(image_files)}: {image_path.name}")
            
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                print(f"  ⚠️  Failed to load image, skipping")
                continue
            
            # Detect faces
            faces = detector.detect(image)
            if not faces:
                print(f"  ⚠️  No faces detected, skipping")
                continue
            
            # Use first detected face
            bbox, confidence = faces[0]
            x1, y1, x2, y2 = bbox
            face_crop = image[y1:y2, x1:x2]
            
            # Extract embedding
            embedding = recognizer.encode(face_crop)
            embedding_array = np.array(embedding, dtype=np.float32)
            
            # Extract attributes
            attributes = attribute_extractor.infer(face_crop)
            
            print(f"  ✅ Detected face with confidence {confidence:.2f}")
            print(f"  📊 Attributes: Age={attributes.get('age')}, "
                  f"Gender={attributes.get('gender')}, "
                  f"Ethnicity={attributes.get('ethnicity')}")
            
            # Create Person record
            person = Person(
                name=f"Person_{idx}",
                age=attributes.get('age', 30),
                gender=attributes.get('gender', 'Unknown'),
                ethnicity=attributes.get('ethnicity', 'Unknown'),
                hair_color=attributes.get('hair_color', 'Unknown'),
                eye_color=attributes.get('eye_color', 'Unknown'),
                skin_tone=attributes.get('skin_tone', 'Unknown'),
                photo_path=str(image_path)
            )
            session.add(person)
            session.flush()  # Get person.id
            
            # Create Embedding record
            embedding_record = Embedding(
                person_id=person.id,
                embedding=embedding_array.tobytes(),
                model_version="arcface_resnet100_v1"
            )
            session.add(embedding_record)
            
            print(f"  💾 Saved Person ID: {person.id}")
        
        # Commit all changes
        session.commit()
        
        # Print summary
        total_persons = session.query(Person).count()
        total_embeddings = session.query(Embedding).count()
        
        print("\n" + "=" * 60)
        print("✅ Database Population Complete!")
        print("=" * 60)
        print(f"Total persons: {total_persons}")
        print(f"Total embeddings: {total_embeddings}")
        print(f"\nNext step: Build FAISS index")
        print("Run: python scripts/build_faiss_index.py")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = populate_database()
        sys.exit(exit_code)
    except Exception as e:
        import traceback
        print(f"\n❌ Error populating database: {e}")
        traceback.print_exc()
        sys.exit(1)
