"""Build FAISS index from database embeddings for fast similarity search."""

import sys
from pathlib import Path
import numpy as np
import faiss
import pickle

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.embedding import Embedding
from app.core.config import settings

def build_faiss_index():
    """Extract embeddings from database and build FAISS IVF-PQ index."""
    
    print("=" * 60)
    print("Building FAISS Index from Database Embeddings")
    print("=" * 60)
    
    # 1. Extract embeddings from database
    print("\n[STEP 1] Extracting embeddings from database...")
    embeddings_list = []
    person_ids = []
    
    with SessionLocal() as session:
        embeddings = session.query(Embedding).all()
        print(f"Found {len(embeddings)} embeddings in database")
        
        for emb in embeddings:
            # Convert binary to numpy array
            embedding_array = np.frombuffer(emb.embedding, dtype=np.float32)
            embeddings_list.append(embedding_array)
            person_ids.append(emb.person_id)
    
    if not embeddings_list:
        print("❌ No embeddings found in database. Please populate database first.")
        print("Run: python scripts/populate_database.py")
        return 1
    
    # 2. Convert to numpy array
    print(f"\n[STEP 2] Converting {len(embeddings_list)} embeddings to numpy array...")
    embeddings_matrix = np.vstack(embeddings_list).astype('float32')
    print(f"Embeddings matrix shape: {embeddings_matrix.shape}")
    
    # 3. Normalize embeddings (important for cosine similarity)
    print("\n[STEP 3] Normalizing embeddings...")
    faiss.normalize_L2(embeddings_matrix)
    
    # 4. Build FAISS index
    print("\n[STEP 4] Building FAISS index...")
    dimension = embeddings_matrix.shape[1]
    n_embeddings = embeddings_matrix.shape[0]
    
    # Choose index type based on dataset size
    if n_embeddings < 1000:
        # For small datasets, use flat index (exact search)
        print(f"Using Flat index (exact search) for {n_embeddings} embeddings")
        index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity after normalization)
    else:
        # For larger datasets, use IVF-PQ for faster approximate search
        nlist = min(100, n_embeddings // 10)  # Number of clusters
        m = 8  # Number of subquantizers
        print(f"Using IVF-PQ index with {nlist} clusters for {n_embeddings} embeddings")
        
        quantizer = faiss.IndexFlatIP(dimension)
        index = faiss.IndexIVFPQ(quantizer, dimension, nlist, m, 8)
        
        # Train the index
        print("Training index...")
        index.train(embeddings_matrix)
    
    # 5. Add embeddings to index
    print("\n[STEP 5] Adding embeddings to index...")
    index.add(embeddings_matrix)
    print(f"✅ Added {index.ntotal} embeddings to index")
    
    # 6. Save index and metadata
    print("\n[STEP 6] Saving index and metadata...")
    index_dir = settings.models_dir / "faiss"
    index_dir.mkdir(exist_ok=True)
    
    index_path = index_dir / "embeddings.index"
    metadata_path = index_dir / "metadata.pkl"
    
    # Save FAISS index
    faiss.write_index(index, str(index_path))
    print(f"✅ Saved FAISS index to {index_path}")
    
    # Save metadata (person_ids mapping)
    metadata = {
        'person_ids': person_ids,
        'dimension': dimension,
        'n_embeddings': n_embeddings,
        'index_type': 'Flat' if n_embeddings < 1000 else 'IVF-PQ'
    }
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"✅ Saved metadata to {metadata_path}")
    
    # 7. Test the index
    print("\n[STEP 7] Testing index with sample query...")
    test_embedding = embeddings_matrix[0:1]  # Use first embedding as test
    k = min(5, n_embeddings)  # Top-k results
    
    distances, indices = index.search(test_embedding, k)
    print(f"Top {k} matches for test query:")
    for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
        print(f"  {i+1}. Person ID: {person_ids[idx]}, Similarity: {dist:.4f}")
    
    print("\n" + "=" * 60)
    print("✅ FAISS Index Built Successfully!")
    print("=" * 60)
    print(f"Index location: {index_path}")
    print(f"Metadata location: {metadata_path}")
    print(f"Total embeddings: {n_embeddings}")
    print(f"Dimension: {dimension}")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = build_faiss_index()
        sys.exit(exit_code)
    except Exception as e:
        import traceback
        print(f"\n❌ Error building FAISS index: {e}")
        traceback.print_exc()
        sys.exit(1)
