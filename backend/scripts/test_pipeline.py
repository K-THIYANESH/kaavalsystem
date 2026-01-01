"""Simple pipeline test to isolate errors."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.pipelines.video_pipeline import VideoPipeline
from app.tasks.state import JobRegistry

async def test_pipeline():
    try:
        print("Creating pipeline...")
        pipeline = VideoPipeline()
        print("✅ Pipeline created")
        
        print("Creating registry...")
        registry = JobRegistry()
        print("✅ Registry created")
        
        print("Adding job...")
        registry.add_job('test_job', total_frames=100)
        print("✅ Job added")
        
        print("Running pipeline...")
        await pipeline.run('test_job', registry)
        print("✅ Pipeline completed successfully!")
        return 0
    except Exception as e:
        import traceback
        print(f"❌ Pipeline failed: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(test_pipeline())
    sys.exit(exit_code)
