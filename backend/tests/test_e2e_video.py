"""End-to-end test for video pipeline."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.pipelines.video_pipeline import VideoPipeline
from app.tasks.state import JobRegistry

async def test_video_pipeline():
    """Test complete video processing pipeline."""
    print("=" * 60)
    print("End-to-End Test: Video Pipeline")
    print("=" * 60)
    
    # Create pipeline and registry
    print("\n[TEST 1] Initializing pipeline...")
    pipeline = VideoPipeline()
    registry = JobRegistry()
    print("✅ Pipeline initialized")
    
    # Add test job
    print("\n[TEST 2] Creating test job...")
    job_id = "test_video_e2e"
    registry.add_job(job_id, total_frames=1000)
    print(f"✅ Job created: {job_id}")
    
    # Run pipeline
    print("\n[TEST 3] Running pipeline...")
    try:
        await pipeline.run(job_id, registry)
        print("✅ Pipeline completed")
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Verify results
    print("\n[TEST 4] Verifying results...")
    job = registry.get(job_id)
    
    if not job:
        print("❌ Job not found in registry")
        return 1
    
    if not job.results:
        print("❌ No results generated")
        return 1
    
    results = job.results
    print(f"✅ Results generated:")
    print(f"  Status: {results.status}")
    print(f"  Matches found: {results.matches_found}")
    print(f"  Processing time: {results.processing_time_seconds:.2f}s")
    print(f"  Timeline events: {len(results.timeline) if results.timeline else 0}")
    
    # Verify pipeline summary
    print("\n[TEST 5] Verifying pipeline summary...")
    if pipeline.last_summary:
        summary = pipeline.last_summary
        print(f"✅ Summary generated:")
        print(f"  Total frames: {summary.total_frames}")
        print(f"  Selected frames: {summary.selected_frames}")
        print(f"  Matches found: {summary.matches_found}")
    else:
        print("⚠️  No summary generated")
    
    print("\n" + "=" * 60)
    print("✅ All Tests Passed!")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(test_video_pipeline())
        sys.exit(exit_code)
    except Exception as e:
        import traceback
        print(f"\n❌ Test failed: {e}")
        traceback.print_exc()
        sys.exit(1)
