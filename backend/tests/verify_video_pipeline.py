import asyncio
import sys
import cv2
import numpy as np
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

print("Importing VideoPipeline...")
from app.pipelines.video_pipeline import VideoPipeline
print("Importing JobRegistry...")
from app.tasks.state import JobRegistry
print("Importing settings...")
from app.core.config import settings
print("Imports done.")

async def verify_pipeline():
    print("=" * 60)
    print("Verification: Video Pipeline with Real File")
    print("=" * 60)

    # 1. Create a dummy video file
    filename = "test_video_gen.mp4"
    filepath = settings.uploads_dir / filename
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n[STEP 1] Generating dummy video at {filepath}...")
    
    width, height = 640, 480
    fps = 30
    duration_sec = 2
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(filepath), fourcc, fps, (width, height))
    
    if not out.isOpened():
        print("❌ Failed to create video writer. Trying .avi...")
        filename = "test_video_gen.avi"
        filepath = settings.uploads_dir / filename
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter(str(filepath), fourcc, fps, (width, height))
        
    if not out.isOpened():
        print("❌ Failed to create video writer.")
        return

    # Write frames with a moving circle (simulating a face)
    for i in range(fps * duration_sec):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        # Moving circle
        cx = int(width/2 + 100 * np.sin(i/10))
        cy = int(height/2)
        cv2.circle(frame, (cx, cy), 50, (0, 255, 0), -1)
        out.write(frame)
    
    out.release()
    print("✅ Dummy video created")

    # 2. Initialize Pipeline
    print("\n[STEP 2] Initializing pipeline...")
    pipeline = VideoPipeline()
    registry = JobRegistry()
    
    # 3. Create Job
    job_id = "verify_job_1"
    # Note: The service usually handles file placement, but here we manually placed it.
    # The pipeline expects job.filename to be the filename in uploads_dir
    registry.add_job(job_id, total_frames=0, filename=filename)
    
    # 4. Run Pipeline
    print(f"\n[STEP 3] Running pipeline for job {job_id}...")
    await pipeline.run(job_id, registry)
    
    # 5. Verify Results
    print("\n[STEP 4] Verifying results...")
    job = registry.get(job_id)
    
    if job.status == "completed":
        print(f"✅ Job completed successfully")
        print(f"  Processed frames: {job.processed_frames}")
        if job.results:
            print(f"  Matches found: {job.results.matches_found}")
            print(f"  Timeline events: {len(job.results.timeline)}")
        else:
            print("⚠️  No results object found")
    else:
        print(f"❌ Job failed with status: {job.status}")
        print(f"  Message: {job.message}")

    # Cleanup
    if filepath.exists():
        try:
            filepath.unlink()
            print("\n✅ Cleanup successful")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(verify_pipeline())
