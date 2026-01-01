# KAAVAL Face Embedding Extraction

This directory contains scripts for extracting and analyzing face embeddings from your person database.

## Overview

The KAAVAL system uses ArcFace to generate 512-dimensional face embeddings. These scripts help you:
- Extract embeddings from all photos in your database
- Analyze embedding quality and statistics
- Visualize embeddings in 2D space
- Compute similarity matrices between persons

## Scripts

### 1. `extract_all_embeddings.py`
Extracts face embeddings from all person folders in `datasets/persons/`.

**Features:**
- Processes multiple photos per person (front view, side views, top/bottom views, various emotions)
- Detects faces using OpenCV Haar Cascade
- Generates 512-d embeddings using ArcFace
- Saves results in both JSON (human-readable) and NumPy (efficient) formats
- Provides detailed progress tracking and error reporting

**Usage:**
```bash
# Basic usage (uses default paths)
python scripts/extract_all_embeddings.py

# Custom paths
python scripts/extract_all_embeddings.py \
    --datasets-dir path/to/datasets/persons \
    --output-dir path/to/output

# Save only JSON format
python scripts/extract_all_embeddings.py --format json

# Save only NumPy format
python scripts/extract_all_embeddings.py --format npy

# Quiet mode (minimal output)
python scripts/extract_all_embeddings.py --quiet
```

**Output Structure:**
```
embeddings_output/
├── extraction_summary.json          # Overall statistics
├── person1_embeddings.json          # Person 1 embeddings + metadata
├── person1_embeddings.npy           # Person 1 embeddings (numpy array)
├── person2_embeddings.json
├── person2_embeddings.npy
└── ...
```

### 2. `analyze_embeddings.py`
Analyzes and visualizes extracted embeddings.

**Features:**
- Computes embedding statistics (norms, intra-person similarity)
- Creates PCA visualization (2D projection)
- Creates t-SNE visualization (2D projection)
- Generates similarity matrix heatmap
- Saves detailed statistics in JSON format

**Usage:**
```bash
# Analyze embeddings
python scripts/analyze_embeddings.py \
    --embeddings-dir embeddings_output

# Custom output directory
python scripts/analyze_embeddings.py \
    --embeddings-dir embeddings_output \
    --output-dir analysis_results
```

**Output:**
```
embeddings_output/analysis/
├── embedding_statistics.json        # Detailed statistics
├── embeddings_pca.png              # PCA visualization
├── embeddings_tsne.png             # t-SNE visualization
└── similarity_matrix.png           # Inter-person similarity heatmap
```

## Requirements

Make sure you have the required dependencies installed:

```bash
pip install numpy opencv-python pillow matplotlib seaborn scikit-learn
```

The ArcFace model should be located at:
```
backend/models/arcface_resnet100.onnx
```

## Workflow

### Step 1: Prepare Your Dataset
Organize your person photos in folders:
```
datasets/persons/
├── person1/
│   ├── person1_front.jpg
│   ├── person1_left.jpg
│   ├── person1_right.jpg
│   ├── person1_smile.jpg
│   └── ...
├── person2/
│   ├── person2_front.jpg
│   └── ...
└── ...
```

### Step 2: Extract Embeddings
```bash
cd backend
python scripts/extract_all_embeddings.py
```

This will:
1. Load the ArcFace model
2. Process each person folder
3. Detect faces in each photo
4. Extract 512-d embeddings
5. Save results to `embeddings_output/`

### Step 3: Analyze Results
```bash
python scripts/analyze_embeddings.py --embeddings-dir embeddings_output
```

This will:
1. Load all extracted embeddings
2. Compute statistics
3. Generate visualizations
4. Save analysis to `embeddings_output/analysis/`

## Understanding the Output

### JSON Format
Each person's JSON file contains:
```json
{
  "person_name": "John Doe",
  "folder_path": "datasets/persons/john_doe",
  "total_images": 7,
  "successful_extractions": 7,
  "failed_extractions": 0,
  "embeddings": [
    {
      "embedding_vector": [0.123, -0.456, ...],  // 512 values
      "metadata": {
        "image_name": "john_doe_front.jpg",
        "bbox": [100, 150, 300, 350],
        "confidence": 1.0,
        "image_size": [480, 640],
        "face_size": [200, 200]
      }
    },
    ...
  ],
  "extraction_timestamp": "2025-11-25T21:40:00"
}
```

### NumPy Format
Each `.npy` file contains a 2D array of shape `(N, 512)` where:
- N = number of successfully processed images
- 512 = embedding dimension

Load with:
```python
import numpy as np
embeddings = np.load('person1_embeddings.npy')
print(embeddings.shape)  # (7, 512)
```

### Statistics
The analysis provides:
- **Intra-person similarity**: How similar are different photos of the same person?
  - Higher values (closer to 1.0) = more consistent embeddings
  - Lower values = more variation (different angles, expressions affect embeddings)
- **Inter-person similarity**: How similar are different persons?
  - Should be lower than intra-person similarity
  - High values might indicate similar-looking people

## Tips

1. **Multiple Views**: Include various angles and expressions for robust embeddings
2. **Quality**: Use clear, well-lit photos for best results
3. **Face Detection**: If face detection fails, ensure faces are clearly visible and not too small
4. **Similarity Threshold**: Typical face recognition uses cosine similarity > 0.6 for matching

## Troubleshooting

**No faces detected:**
- Ensure faces are clearly visible
- Check image quality and lighting
- Verify face is not too small or occluded

**Model not found:**
- Run `python scripts/download_models.py` to download the ArcFace model
- Verify model exists at `backend/models/arcface_resnet100.onnx`

**Out of memory:**
- Process persons in batches
- Use `--format npy` to save only NumPy arrays (smaller)

## Integration with KAAVAL

These embeddings can be used to:
1. Populate the database with person records
2. Build a FAISS index for fast similarity search
3. Train or fine-tune face recognition models
4. Evaluate system performance
5. Debug face matching issues
