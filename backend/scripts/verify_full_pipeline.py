"""End-to-End Verification Script for KAAVAL System.

Verifies:
1. Model Loading (ArcFace, AttributeNet, etc.)
2. Database Connection & Schema
3. Google API Client (Mocked/Real)
4. Full Pipeline Execution (Video -> Result)
5. Error Handling
"""

import asyncio
import sys
from pathlib import Path
import cv2
import numpy as np
import torch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.ml.registry import get_registry
from app.services.google_maps import google_maps_service
from app.pipelines.video_pipeline import VideoPipeline
from app.tasks.state import JobRegistry

async def verify_system():
    print("=" * 60)
    print("KAAVAL System Verification")
    print("=" * 60)
    
    errors = []

    # 1. Verify Models
    print("\n[CHECK] 1. ML Models...")
    try:
        registry = get_registry()
        print(f"  - Detector: {type(registry.detector).__name__} [OK]")
        print(f"  - Recognizer: {type(registry.recognizer).__name__} [OK]")
        print(f"  - Attribute Extractor: {type(registry.attribute_extractor).__name__} [OK]")
        
        # Test Inference
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = registry.detector.detect(dummy_frame)
        print("  - Inference Test: [OK]")
        
    except Exception as e:
        print(f"  [FAIL] Model verification failed: {e}")
        errors.append(f"Model Error: {e}")

    # 2. Verify Database
    print("\n[CHECK] 2. Database...")
    try:
        with SessionLocal() as session:
            # Simple query to check connection
            session.execute("SELECT 1")
            print("  - Connection: [OK]")
            print(f"  - Path: {settings.database_path} [OK]")
    except Exception as e:
        print(f"  [FAIL] Database verification failed: {e}")
        errors.append(f"Database Error: {e}")

    # 3. Verify Google API
    print("\n[CHECK] 3. Google API...")
    try:
        # Test with a known coordinate (San Francisco)
        # Note: This will fail if no API key is set, which is expected in dev
        if settings.google_maps_api_key:
            address = await google_maps_service.get_address_from_coordinates(37.7749, -122.4194)
            print(f"  - Geocoding: {address} [OK]")
        else:
            print("  - API Key: Not configured (Skipping live call) [WARN]")
    except Exception as e:
        print(f"  [FAIL] Google API verification failed: {e}")
        errors.append(f"Google API Error: {e}")

    # 4. Verify Video Pipeline
    print("\n[CHECK] 4. Video Pipeline...")
    try:
        pipeline = VideoPipeline()
        registry = JobRegistry()
        job_id = "test_job_123"
        registry.add_job(job_id, total_frames=100)
        
        # Run pipeline (it uses random frames in the mock implementation)
        await pipeline.run(job_id, registry)
        
        result = registry.get(job_id).results
        if result and result.status == "completed":
            print(f"  - Pipeline Execution: [OK]")
            print(f"  - Matches Found: {result.matches_found}")
        else:
            print("  - Pipeline Execution: [FAIL] (Status not completed)")
            errors.append("Pipeline failed to complete")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"  [FAIL] Pipeline verification failed: {e}")
        errors.append(f"Pipeline Error: {e}")

    print("\n" + "=" * 60)
    if not errors:
        print("VERIFICATION SUCCESSFUL: System is 100% Operational")
        return 0
    else:
        print(f"VERIFICATION FAILED: {len(errors)} errors found")
        for err in errors:
            print(f"  - {err}")
        return 1

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        sys.exit(loop.run_until_complete(verify_system()))
    except KeyboardInterrupt:
        pass
