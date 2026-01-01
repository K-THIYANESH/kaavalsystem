"""
KAAVAL Face Embedding Extraction Script
Extracts embeddings from all photos in the datasets/persons/ folder.
Each person folder contains multiple photos with different views and emotions.
"""
import os
import sys
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import cv2
from PIL import Image

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ml.recognizers.arcface import ArcFaceRecognizer


def detect_faces_opencv(image: np.ndarray) -> List[Dict]:
    """Detect faces using OpenCV Haar Cascade.
    
    Args:
        image: Input image as numpy array (RGB)
        
    Returns:
        List of face detections with bbox and confidence
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    # Load Haar Cascade (built into OpenCV)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    # Convert to list of dicts with bbox
    results = []
    for (x, y, w, h) in faces:
        results.append({
            'bbox': [x, y, x+w, y+h],
            'confidence': 1.0
        })
    
    return results


def extract_embedding_from_image(
    image_path: Path,
    recognizer: ArcFaceRecognizer
) -> Optional[Tuple[np.ndarray, Dict]]:
    """Extract face embedding from a single image.
    
    Args:
        image_path: Path to the image file
        recognizer: ArcFace recognizer instance
        
    Returns:
        Tuple of (embedding vector, metadata) or None if failed
    """
    try:
        # Load image
        img = Image.open(image_path).convert('RGB')
        img_array = np.array(img)
        
        # Detect face
        faces = detect_faces_opencv(img_array)
        
        if not faces or len(faces) == 0:
            return None
        
        # Get embedding from first (largest) face
        face = faces[0]
        bbox = face['bbox']
        x1, y1, x2, y2 = bbox
        
        # Crop face region
        face_crop = img_array[y1:y2, x1:x2]
        
        # Convert RGB to BGR for OpenCV processing
        face_crop_bgr = cv2.cvtColor(face_crop, cv2.COLOR_RGB2BGR)
        
        # Extract embedding using ArcFace
        embedding = recognizer.encode(face_crop_bgr)
        embedding_array = np.array(embedding, dtype=np.float32)
        
        # Create metadata
        metadata = {
            'image_name': image_path.name,
            'image_path': str(image_path),
            'bbox': [int(x) for x in bbox],  # Convert to Python int for JSON serialization
            'confidence': float(face['confidence']),
            'image_size': [int(x) for x in img_array.shape[:2]],
            'face_size': [int(x) for x in face_crop.shape[:2]]
        }
        
        return embedding_array, metadata
        
    except Exception as e:
        print(f"    ⚠️  Error processing {image_path.name}: {str(e)[:60]}")
        return None



def extract_person_embeddings(
    person_folder: Path,
    recognizer: ArcFaceRecognizer,
    verbose: bool = True
) -> Dict:
    """Extract all embeddings for a single person.
    
    Args:
        person_folder: Path to person's folder containing images
        recognizer: ArcFace recognizer instance
        verbose: Whether to print progress
        
    Returns:
        Dictionary containing person data and all embeddings
    """
    person_name = person_folder.name.replace("_", " ").title()
    
    # Get all image files
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
        image_files.extend(person_folder.glob(ext))
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Processing: {person_name}")
        print(f"{'='*60}")
        print(f"Found {len(image_files)} images")
    
    embeddings_data = {
        'person_name': person_name,
        'folder_path': str(person_folder),
        'total_images': len(image_files),
        'successful_extractions': 0,
        'failed_extractions': 0,
        'embeddings': [],
        'extraction_timestamp': datetime.now().isoformat()
    }
    
    # Process each image
    for idx, img_path in enumerate(image_files, 1):
        if verbose:
            print(f"  [{idx}/{len(image_files)}] {img_path.name}...", end=" ")
        
        result = extract_embedding_from_image(img_path, recognizer)
        
        if result is not None:
            embedding, metadata = result
            embeddings_data['embeddings'].append({
                'embedding_vector': embedding.tolist(),
                'metadata': metadata
            })
            embeddings_data['successful_extractions'] += 1
            if verbose:
                print("✅ SUCCESS")
        else:
            embeddings_data['failed_extractions'] += 1
            if verbose:
                print("❌ FAILED (no face detected)")
    
    if verbose:
        print(f"\nSummary for {person_name}:")
        print(f"  ✅ Successful: {embeddings_data['successful_extractions']}")
        print(f"  ❌ Failed: {embeddings_data['failed_extractions']}")
    
    return embeddings_data


def save_embeddings(
    person_data: Dict,
    output_dir: Path,
    save_format: str = 'both'
) -> None:
    """Save embeddings to disk.
    
    Args:
        person_data: Dictionary containing person embeddings data
        output_dir: Directory to save embeddings
        save_format: 'json', 'npy', or 'both'
    """
    person_name = person_data['person_name'].lower().replace(" ", "_")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as JSON (human-readable, includes metadata)
    if save_format in ['json', 'both']:
        json_path = output_dir / f"{person_name}_embeddings.json"
        with open(json_path, 'w') as f:
            json.dump(person_data, f, indent=2)
        print(f"  💾 Saved JSON: {json_path}")
    
    # Save as NumPy (efficient, for ML pipelines)
    if save_format in ['npy', 'both']:
        embeddings_array = np.array([
            emb['embedding_vector'] 
            for emb in person_data['embeddings']
        ])
        npy_path = output_dir / f"{person_name}_embeddings.npy"
        np.save(npy_path, embeddings_array)
        print(f"  💾 Saved NumPy: {npy_path} (shape: {embeddings_array.shape})")


def extract_all_embeddings(
    datasets_dir: Path,
    output_dir: Path,
    save_format: str = 'both',
    verbose: bool = True
) -> Dict:
    """Extract embeddings from all persons in the database.
    
    Args:
        datasets_dir: Path to datasets/persons/ directory
        output_dir: Directory to save extracted embeddings
        save_format: 'json', 'npy', or 'both'
        verbose: Whether to print progress
        
    Returns:
        Summary statistics dictionary
    """
    print("="*60)
    print("KAAVAL FACE EMBEDDING EXTRACTION")
    print("="*60)
    
    # Initialize recognizer
    print("\n🔧 Loading ArcFace recognizer...")
    try:
        recognizer = ArcFaceRecognizer(weights_path="models/arcface_resnet100.onnx")
        
        if not hasattr(recognizer, '_session') or recognizer._session is None:
            print("❌ ERROR: Failed to load face recognizer model")
            print("Make sure models/arcface_resnet100.onnx exists")
            return {}
        
        print("✅ Face recognizer loaded successfully")
    except Exception as e:
        print(f"❌ ERROR: Failed to load models: {e}")
        return {}
    
    # Get all person folders
    if not datasets_dir.exists():
        print(f"\n❌ ERROR: Directory not found: {datasets_dir}")
        return {}
    
    person_folders = sorted([f for f in datasets_dir.iterdir() if f.is_dir()])
    
    if not person_folders:
        print(f"\n❌ ERROR: No person folders found in {datasets_dir}")
        return {}
    
    print(f"\n📁 Found {len(person_folders)} person folders")
    print(f"📂 Output directory: {output_dir}")
    
    # Process each person
    all_results = []
    total_images = 0
    total_successful = 0
    total_failed = 0
    
    for person_folder in person_folders:
        person_data = extract_person_embeddings(
            person_folder,
            recognizer,
            verbose=verbose
        )
        
        # Save embeddings
        save_embeddings(person_data, output_dir, save_format)
        
        # Update statistics
        all_results.append(person_data)
        total_images += person_data['total_images']
        total_successful += person_data['successful_extractions']
        total_failed += person_data['failed_extractions']
    
    # Save summary
    summary = {
        'extraction_timestamp': datetime.now().isoformat(),
        'total_persons': len(person_folders),
        'total_images': total_images,
        'total_successful': total_successful,
        'total_failed': total_failed,
        'success_rate': f"{(total_successful/total_images*100):.1f}%" if total_images > 0 else "0%",
        'persons': [
            {
                'name': p['person_name'],
                'successful': p['successful_extractions'],
                'failed': p['failed_extractions'],
                'total': p['total_images']
            }
            for p in all_results
        ]
    }
    
    summary_path = output_dir / "extraction_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Print final summary
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    print(f"Total Persons:     {summary['total_persons']}")
    print(f"Total Images:      {summary['total_images']}")
    print(f"✅ Successful:     {summary['total_successful']}")
    print(f"❌ Failed:         {summary['total_failed']}")
    print(f"Success Rate:      {summary['success_rate']}")
    print(f"\n💾 Summary saved: {summary_path}")
    print("="*60)
    
    return summary


def main():
    """Main entry point."""
    # Setup paths
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    datasets_dir = backend_dir / "datasets" / "persons"
    output_dir = backend_dir / "embeddings_output"
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description="Extract face embeddings from all persons in the database"
    )
    parser.add_argument(
        '--datasets-dir',
        type=str,
        default=str(datasets_dir),
        help='Path to datasets/persons directory'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default=str(output_dir),
        help='Directory to save extracted embeddings'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['json', 'npy', 'both'],
        default='both',
        help='Output format: json (human-readable), npy (numpy array), or both'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress verbose output'
    )
    
    args = parser.parse_args()
    
    # Run extraction
    extract_all_embeddings(
        datasets_dir=Path(args.datasets_dir),
        output_dir=Path(args.output_dir),
        save_format=args.format,
        verbose=not args.quiet
    )


if __name__ == "__main__":
    main()
