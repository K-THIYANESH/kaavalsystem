"""Test ArcFace model loading"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ml.recognizers.arcface import ArcFaceRecognizer
import numpy as np
import cv2

print("="*60)
print("Testing ArcFace Model")
print("="*60)

# Test model loading
print("\n1. Loading ArcFace model...")
recognizer = ArcFaceRecognizer(weights_path="models/arcface_resnet100.onnx")

if hasattr(recognizer, '_session') and recognizer._session is not None:
    print("✅ Model loaded successfully!")
    print(f"   Input name: {recognizer._input_name}")
    print(f"   Embedding size: {recognizer.embedding_size}")
else:
    print("❌ Model failed to load!")
    sys.exit(1)

# Test with a dummy image
print("\n2. Testing with dummy image...")
dummy_face = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
embedding = recognizer.encode(dummy_face)

print(f"   Embedding type: {type(embedding)}")
print(f"   Embedding length: {len(embedding)}")
print(f"   First 10 values: {embedding[:10]}")
print(f"   Sum of embedding: {sum(embedding)}")

if sum(embedding) == 0:
    print("❌ WARNING: Embedding is all zeros!")
else:
    print("✅ Embedding contains non-zero values")

print("\n" + "="*60)
