"""End-to-end test for camera service."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.camera_service import CameraService
from app.schemas.camera import CameraStartRequest

async def test_camera_service():
    """Test camera service initialization and streaming."""
    print("=" * 60)
    print("End-to-End Test: Camera Service")
    print("=" * 60)
    
    # Create service
    print("\n[TEST 1] Creating camera service...")
    service = CameraService()
    print("✅ Service created")
    
    # Check initial status
    print("\n[TEST 2] Checking initial status...")
    status = await service.get_status()
    print(f"✅ Initial status: {status['status']}")
    assert status['status'] == 'idle', "Initial status should be idle"
    
    # Start stream
    print("\n[TEST 3] Starting camera stream...")
    payload = CameraStartRequest(device_id=0, frame_skip=3)
    await service.start_stream(payload)
    
    # Wait for stream to initialize
    await asyncio.sleep(2)
    
    # Check running status
    print("\n[TEST 4] Checking running status...")
    status = await service.get_status()
    print(f"✅ Running status: {status['status']}")
    print(f"  FPS: {status.get('fps', 0)}")
    print(f"  Active matches: {status.get('active_matches', 0)}")
    assert status['status'] in ['running', 'initializing'], "Status should be running or initializing"
    
    # Test frame streaming
    print("\n[TEST 5] Testing frame streaming...")
    frame_count = 0
    async for frame_data in service.stream_frames():
        frame_count += 1
        if frame_count >= 5:  # Get 5 frames
            break
    print(f"✅ Received {frame_count} frames")
    assert frame_count == 5, "Should receive 5 frames"
    
    # Stop stream
    print("\n[TEST 6] Stopping camera stream...")
    await service.stop_stream()
    
    # Wait for cleanup
    await asyncio.sleep(1)
    
    # Check stopped status
    print("\n[TEST 7] Checking stopped status...")
    status = await service.get_status()
    print(f"✅ Stopped status: {status['status']}")
    assert status['status'] in ['idle', 'stopped'], "Status should be idle or stopped"
    
    print("\n" + "=" * 60)
    print("✅ All Tests Passed!")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(test_camera_service())
        sys.exit(exit_code)
    except Exception as e:
        import traceback
        print(f"\n❌ Test failed: {e}")
        traceback.print_exc()
        sys.exit(1)
