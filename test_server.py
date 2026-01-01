"""Quick server test to verify all imports work."""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

print("Testing imports...")

try:
    from app.main import app
    print("✓ FastAPI app imported successfully")
    print("✓ All dependencies are working")
    print("\n✅ Server is ready to start!")
    print("\nRun: .\\start_project.ps1")
except Exception as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
