"""Performance benchmarks for KAAVAL system."""

import sys
from pathlib import Path
import time
import numpy as np
from statistics import mean, median

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ml.registry import get_registry
from app.ml.matching.coarse_to_fine import CoarseToFineMatcher
from app.core.database import SessionLocal
from app.models.embedding import Embedding

def benchmark_embedding_extraction():
    """Benchmark face embedding extraction speed."""
    print("\n" + "=" * 60)
    print("Benchmark: Embedding Extraction")
    print("=" * 60)
    
    registry = get_registry(enable_age_progression=False)
    
    # Generate random face images
    n_samples = 100
    latencies = []
    
    print(f"Extracting embeddings for {n_samples} random face crops...")
    for i in range(n_samples):
        # Simulate 112x112 face crop
        face_crop = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
        
        start = time.perf_counter()
        embedding = registry.recognizer.encode(face_crop)
        latency = (time.perf_counter() - start) * 1000  # Convert to ms
        latencies.append(latency)
        
        if (i + 1) % 20 == 0:
            print(f"  Processed {i + 1}/{n_samples}")
    
    # Calculate statistics
    p50 = median(latencies)
    p90 = np.percentile(latencies, 90)
    p99 = np.percentile(latencies, 99)
    avg = mean(latencies)
    
    print(f"\n📊 Results:")
    print(f"  Average: {avg:.2f} ms")
    print(f"  P50 (median): {p50:.2f} ms")
    print(f"  P90: {p90:.2f} ms")
    print(f"  P99: {p99:.2f} ms")
    print(f"  Throughput: {1000/avg:.1f} embeddings/sec")
    
    return {
        'avg': avg,
        'p50': p50,
        'p90': p90,
        'p99': p99
    }

def benchmark_faiss_search():
    """Benchmark FAISS similarity search speed."""
    print("\n" + "=" * 60)
    print("Benchmark: FAISS Similarity Search")
    print("=" * 60)
    
    matcher = CoarseToFineMatcher()
    
    if not matcher._loaded:
        print("❌ FAISS index not loaded. Run: python scripts/build_faiss_index.py")
        return None
    
    # Get sample embeddings from database
    with SessionLocal() as session:
        embeddings = session.query(Embedding).limit(100).all()
        if not embeddings:
            print("❌ No embeddings in database. Run: python scripts/populate_database.py")
            return None
        
        print(f"Testing with {len(embeddings)} query embeddings...")
        
        latencies = []
        for i, emb in enumerate(embeddings):
            embedding_array = np.frombuffer(emb.embedding, dtype=np.float32)
            
            start = time.perf_counter()
            results = matcher.coarse_filter(embedding_array.tolist())
            latency = (time.perf_counter() - start) * 1000  # Convert to ms
            latencies.append(latency)
            
            if (i + 1) % 20 == 0:
                print(f"  Processed {i + 1}/{len(embeddings)}")
        
        # Calculate statistics
        p50 = median(latencies)
        p90 = np.percentile(latencies, 90)
        p99 = np.percentile(latencies, 99)
        avg = mean(latencies)
        
        print(f"\n📊 Results:")
        print(f"  Average: {avg:.2f} ms")
        print(f"  P50 (median): {p50:.2f} ms")
        print(f"  P90: {p90:.2f} ms")
        print(f"  P99: {p99:.2f} ms")
        print(f"  Throughput: {1000/avg:.1f} searches/sec")
        
        # Check if P90 meets target
        target_p90 = 100  # ms
        if p90 < target_p90:
            print(f"  ✅ P90 latency ({p90:.2f} ms) meets target (< {target_p90} ms)")
        else:
            print(f"  ⚠️  P90 latency ({p90:.2f} ms) exceeds target (< {target_p90} ms)")
        
        return {
            'avg': avg,
            'p50': p50,
            'p90': p90,
            'p99': p99
        }

def benchmark_attribute_extraction():
    """Benchmark attribute extraction speed."""
    print("\n" + "=" * 60)
    print("Benchmark: Attribute Extraction")
    print("=" * 60)
    
    registry = get_registry(enable_age_progression=False)
    
    # Generate random face images
    n_samples = 100
    latencies = []
    
    print(f"Extracting attributes for {n_samples} random face crops...")
    for i in range(n_samples):
        # Simulate 224x224 face crop
        face_crop = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        start = time.perf_counter()
        attributes = registry.attribute_extractor.infer(face_crop)
        latency = (time.perf_counter() - start) * 1000  # Convert to ms
        latencies.append(latency)
        
        if (i + 1) % 20 == 0:
            print(f"  Processed {i + 1}/{n_samples}")
    
    # Calculate statistics
    p50 = median(latencies)
    p90 = np.percentile(latencies, 90)
    p99 = np.percentile(latencies, 99)
    avg = mean(latencies)
    
    print(f"\n📊 Results:")
    print(f"  Average: {avg:.2f} ms")
    print(f"  P50 (median): {p50:.2f} ms")
    print(f"  P90: {p90:.2f} ms")
    print(f"  P99: {p99:.2f} ms")
    
    return {
        'avg': avg,
        'p50': p50,
        'p90': p90,
        'p99': p99
    }

def run_all_benchmarks():
    """Run all performance benchmarks."""
    print("=" * 60)
    print("KAAVAL Performance Benchmarks")
    print("=" * 60)
    
    results = {}
    
    # Run benchmarks
    results['embedding'] = benchmark_embedding_extraction()
    results['faiss'] = benchmark_faiss_search()
    results['attributes'] = benchmark_attribute_extraction()
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    print("\n📈 Latency (P90):")
    if results['embedding']:
        print(f"  Embedding Extraction: {results['embedding']['p90']:.2f} ms")
    if results['faiss']:
        print(f"  FAISS Search: {results['faiss']['p90']:.2f} ms")
    if results['attributes']:
        print(f"  Attribute Extraction: {results['attributes']['p90']:.2f} ms")
    
    print("\n🚀 Throughput:")
    if results['embedding']:
        print(f"  Embeddings: {1000/results['embedding']['avg']:.1f} /sec")
    if results['faiss']:
        print(f"  Searches: {1000/results['faiss']['avg']:.1f} /sec")
    
    print("\n✅ Benchmarks Complete!")

if __name__ == "__main__":
    try:
        run_all_benchmarks()
    except Exception as e:
        import traceback
        print(f"\n❌ Benchmark failed: {e}")
        traceback.print_exc()
        sys.exit(1)
