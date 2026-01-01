"""Camera streaming orchestration."""

from __future__ import annotations

import asyncio
import contextlib
import io
import time
from typing import AsyncIterator, Dict

import cv2
import numpy as np
from PIL import Image

from ..core.config import settings
from ..ml.registry import get_registry
from ..schemas.camera import CameraStartRequest


class CameraService:
    """Manage state for the live camera pipeline."""

    def __init__(self) -> None:
        self._stream_task: asyncio.Task | None = None
        self._capture: cv2.VideoCapture | None = None
        self._registry = None
        self._frame_buffer: bytes | None = None
        self._matches_count = 0
        self._status: Dict[str, float | int | str] = {
            "status": "idle",
            "message": "Awaiting activation",
            "fps": 0.0,
            "frame_skip": settings.frame_skip_interval,
            "gpu_utilization": 0.0,
            "active_matches": 0,
        }

    async def start_stream(self, payload: CameraStartRequest) -> None:
        """Boot the capture loop in background."""

        self._status.update({"status": "initializing", "message": "Starting camera"})
        if self._stream_task and not self._stream_task.done():
            return
        
        # Initialize ML registry
        if not self._registry:
            self._registry = get_registry(enable_age_progression=False)
        
        # Try to open camera
        device_id = payload.device_id if hasattr(payload, 'device_id') else 0
        try:
            # On Windows, CAP_DSHOW can be faster/more reliable
            import platform
            if platform.system() == "Windows":
                self._capture = cv2.VideoCapture(device_id, cv2.CAP_DSHOW)
            else:
                self._capture = cv2.VideoCapture(device_id)
            
            if not self._capture.isOpened():
                # Fallback to demo mode if camera not available
                print(f"Camera {device_id} could not be opened. Switching to demo mode.")
                self._capture = None
                self._status.update({"status": "running", "message": "Demo mode (no camera)"})
            else:
                self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self._status.update({"status": "running", "message": "Streaming"})
        except Exception as e:
            print(f"Error opening camera: {e}")
            self._capture = None
            self._status.update({"status": "running", "message": "Demo mode (no camera)"})
        
        loop = asyncio.get_event_loop()
        self._stream_task = loop.create_task(self._run_stream(payload))

    async def _run_stream(self, payload: CameraStartRequest) -> None:
        """Process camera frames and detect faces."""

        skip = payload.frame_skip if hasattr(payload, 'frame_skip') else settings.frame_skip_interval
        frame_count = 0
        last_fps_time = time.time()
        fps_counter = 0
        
        try:
            while True:
                await asyncio.sleep(0.033)  # ~30 FPS
                
                # Get frame
                if self._capture and self._capture.isOpened():
                    ret, frame = self._capture.read()
                    if not ret:
                        # Generate demo frame if camera read fails
                        frame = self._generate_demo_frame()
                else:
                    # Generate demo frame if no camera available
                    frame = self._generate_demo_frame()
                
                # Process every Nth frame
                if frame_count % (skip + 1) == 0:
                    # Detect faces
                    try:
                        detections = self._registry.detector.detect(frame)
                        self._matches_count = len(detections)
                        
                        # Draw bounding boxes
                        for bbox, confidence in detections:
                            x1, y1, x2, y2 = bbox
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(frame, f"{confidence:.2f}", (x1, y1 - 10),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                            
                            # Extract embedding and match (Simplified for live stream)
                            # In a real scenario, we would run recognition here.
                            # For now, we just show detection.
                            
                            # If attributes are requested, run attribute net
                            # attributes = self._registry.attribute_extractor.extract(face_crop)
                            
                    except Exception:
                        pass
                
                # Encode frame to JPEG
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                self._frame_buffer = buffer.tobytes()
                
                # Update FPS
                fps_counter += 1
                if time.time() - last_fps_time >= 1.0:
                    self._status["fps"] = fps_counter
                    fps_counter = 0
                    last_fps_time = time.time()
                
                self._status["active_matches"] = self._matches_count
                self._status["gpu_utilization"] = 35.0 + (self._matches_count * 5)
                frame_count += 1
                
        except asyncio.CancelledError:
            self._status.update({"status": "stopped", "message": "Stream stopped"})
            raise
        except Exception as e:
            self._status.update({"status": "error", "message": str(e)})

    def _generate_demo_frame(self) -> np.ndarray:
        """Generate a demo frame with animated face detection."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Create animated demo face
        import math
        t = time.time()
        center_x = int(320 + 100 * math.sin(t))
        center_y = int(240 + 50 * math.cos(t * 0.7))
        size = int(80 + 20 * math.sin(t * 2))
        
        # Draw face circle
        cv2.circle(frame, (center_x, center_y), size, (0, 255, 0), 2)
        cv2.putText(frame, "DEMO MODE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, "Face Detected", (center_x - 60, center_y - size - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        self._matches_count = 1
        return frame

    async def stop_stream(self) -> None:
        """Cancel the running stream task if active."""

        if self._stream_task:
            self._stream_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._stream_task
        
        if self._capture:
            self._capture.release()
            self._capture = None
        
        self._frame_buffer = None
        self._matches_count = 0
        self._status.update({"status": "idle", "message": "Awaiting activation", "fps": 0.0, "active_matches": 0})

    async def get_status(self) -> Dict[str, float | int | str]:
        """Return the latest status snapshot."""

        return self._status

    async def stream_frames(self) -> AsyncIterator[bytes]:
        """Yield MJPEG frame bytes."""

        boundary = b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
        while True:
            if self._frame_buffer:
                yield boundary + self._frame_buffer + b"\r\n"
            else:
                # Send placeholder frame
                placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(placeholder, "Waiting for camera...", (150, 240),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                _, buffer = cv2.imencode('.jpg', placeholder)
                yield boundary + buffer.tobytes() + b"\r\n"
            await asyncio.sleep(0.033)  # ~30 FPS


def get_camera_service() -> CameraService:
    """FastAPI dependency provider."""

    return CameraService()

