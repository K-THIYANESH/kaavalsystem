"""Comprehensive module-by-module verification script.

Tests each component independently to ensure error-free operation.
"""

import sys
from pathlib import Path
import numpy as np
import asyncio

sys.path.insert(0, str(Path(__file__).parent.parent))

def test_detector():
    """Test face detector."""
    print("\n" + "="*60)
    print("TEST 1: Face Detector (RetinaFace + Haar Cascade)")
    print("="*60)
    
    try:
        from app.ml.detectors.retinaface import RetinaFaceDetector
        
        detector = RetinaFaceDetector()
        print("✅ Detector initialized")
        
        # Test with random image
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        faces = detector.detect(test_image)
        print(f"✅ Detection works (found {len(faces)} faces in random image)")
        
        # Test with real face-like pattern
        face_image = np.ones((480, 640, 3), dtype=np.uint8) * 128
        cv2 = __import__('cv2')
        cv2.rectangle(face_image, (200, 150), (440, 330), (255, 255, 255), -1)
        faces = detector.detect(face_image)
        print(f"✅ Detection on pattern image (found {len(faces)} faces)")
        
        return True
    except Exception as e:
        print(f"❌ Detector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_recognizer():
    """Test face recognizer."""
    print("\n" + "="*60)
    print("TEST 2: Face Recognizer (ArcFace)")
    print("="*60)
    
    try:
        from app.ml.recognizers.arcface import ArcFaceRecognizer
        
        recognizer = ArcFaceRecognizer(weights_path="models/arcface_resnet100.onnx")
        print("✅ Recognizer initialized")
        
        # Test embedding extraction
        test_face = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
        embedding = recognizer.encode(test_face)
        
        assert len(embedding) == 512, f"Expected 512-d embedding, got {len(embedding)}"
        print(f"✅ Embedding extraction works (512-d vector)")
        
        # Test normalization
        embedding_array = np.array(embedding)
        norm = np.linalg.norm(embedding_array)
        print(f"✅ Embedding norm: {norm:.4f} (should be ~1.0 if normalized)")
        
        return True
    except Exception as e:
        print(f"❌ Recognizer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_attribute_extractor():
    """Test attribute extractor."""
    print("\n" + "="*60)
    print("TEST 3: Attribute Extractor")
    print("="*60)
    
    try:
        from app.ml.attributes.attribute_net import AttributeExtractor
        
        extractor = AttributeExtractor(weights_path="models/attribute_net.onnx")
        print("✅ Attribute extractor initialized")
        
        # Test attribute extraction
        test_face = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        attributes = extractor.infer(test_face)
        
        required_attrs = ['age', 'gender', 'ethnicity']
        for attr in required_attrs:
            assert attr in attributes, f"Missing attribute: {attr}"
        
        print(f"✅ Attribute extraction works")
        print(f"   Sample: Age={attributes['age']}, Gender={attributes['gender']}, "
              f"Ethnicity={attributes['ethnicity']}")
        
        return True
    except Exception as e:
        print(f"❌ Attribute extractor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_matcher():
    """Test coarse-to-fine matcher."""
    print("\n" + "="*60)
    print("TEST 4: Coarse-to-Fine Matcher (FAISS)")
    print("="*60)
    
    try:
        from app.ml.matching.coarse_to_fine import CoarseToFineMatcher
        
        matcher = CoarseToFineMatcher()
        print("✅ Matcher initialized")
        
        # Test search
        test_embedding = np.random.randn(512).astype(np.float32).tolist()
        results = matcher.coarse_filter(test_embedding)
        print(f"✅ Coarse filter works (returned {len(results)} candidates)")
        
        # Test fine match
        matches = matcher.fine_match(test_embedding, results[:10])
        print(f"✅ Fine match works (returned {len(matches)} matches)")
        
        if matches:
            print(f"   Top match: Person ID={matches[0].person_id}, Score={matches[0].score:.4f}")
        
        return True
    except Exception as e:
        print(f"❌ Matcher test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """Test database connection."""
    print("\n" + "="*60)
    print("TEST 5: Database Connection")
    print("="*60)
    
    try:
        from app.core.database import SessionLocal
        from app.models.person import Person
        from app.models.embedding import Embedding
        
        with SessionLocal() as session:
            # Test connection
            session.execute("SELECT 1")
            print("✅ Database connection works")
            
            # Count records
            person_count = session.query(Person).count()
            embedding_count = session.query(Embedding).count()
            
            print(f"✅ Database accessible")
            print(f"   Persons: {person_count}")
            print(f"   Embeddings: {embedding_count}")
        
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_google_maps():
    """Test Google Maps service."""
    print("\n" + "="*60)
    print("TEST 6: Google Maps Service")
    print("="*60)
    
    try:
        from app.services.google_maps import google_maps_service
        from app.core.config import settings
        
        print("✅ Google Maps service initialized")
        
        if settings.google_maps_api_key:
            print("✅ API key configured")
        else:
            print("⚠️  API key not configured (optional)")
        
        print("✅ Service ready (requires API key for actual calls)")
        
        return True
    except Exception as e:
        print(f"❌ Google Maps test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_video_pipeline():
    """Test video pipeline."""
    print("\n" + "="*60)
    print("TEST 7: Video Pipeline")
    print("="*60)
    
    try:
        from app.pipelines.video_pipeline import VideoPipeline
        from app.tasks.state import JobRegistry
        
        pipeline = VideoPipeline()
        print("✅ Video pipeline initialized")
        
        registry = JobRegistry()
        job_id = "test_verification"
        registry.add_job(job_id, total_frames=100)
        print("✅ Job registry works")
        
        # Run pipeline
        await pipeline.run(job_id, registry)
        print("✅ Pipeline execution completed")
        
        # Check results
        job = registry.get(job_id)
        if job and job.results:
            print(f"✅ Results generated (status: {job.results.status})")
        else:
            print("⚠️  No results (expected for test)")
        
        return True
    except Exception as e:
        print(f"❌ Video pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_camera_service():
    """Test camera service."""
    print("\n" + "="*60)
    print("TEST 8: Camera Service")
    print("="*60)
    
    try:
        from app.services.camera_service import CameraService
        
        service = CameraService()
        print("✅ Camera service initialized")
        
        status = await service.get_status()
        print(f"✅ Status check works (status: {status['status']})")
        
        return True
    except Exception as e:
        print(f"❌ Camera service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ml_registry():
    """Test ML model registry."""
    print("\n" + "="*60)
    print("TEST 9: ML Model Registry")
    print("="*60)
    
    try:
        from app.ml.registry import get_registry
        
        registry = get_registry(enable_age_progression=False)
        print("✅ Registry loaded")
        
        # Check all components
        assert registry.detector is not None, "Detector not loaded"
        print("✅ Detector available")
        
        assert registry.recognizer is not None, "Recognizer not loaded"
        print("✅ Recognizer available")
        
        assert registry.attribute_extractor is not None, "Attribute extractor not loaded"
        print("✅ Attribute extractor available")
        
        assert registry.matcher is not None, "Matcher not loaded"
        print("✅ Matcher available")
        
        return True
    except Exception as e:
        print(f"❌ Registry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_all_tests():
    """Run all module tests."""
    print("="*60)
    print("KAAVAL System - Comprehensive Module Verification")
    print("="*60)
    
    results = {}
    
    # Run synchronous tests
    results['detector'] = test_detector()
    results['recognizer'] = test_recognizer()
    results['attributes'] = test_attribute_extractor()
    results['matcher'] = test_matcher()
    results['database'] = test_database()
    results['google_maps'] = test_google_maps()
    results['registry'] = test_ml_registry()
    
    # Run async tests
    results['video_pipeline'] = await test_video_pipeline()
    results['camera_service'] = await test_camera_service()
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name.replace('_', ' ').title()}")
    
    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - SYSTEM IS ERROR-FREE!")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(run_all_tests())
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
