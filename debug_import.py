import sys
sys.path.insert(0, 'backend')

try:
    print("Importing routes...")
    from app.api.routes import api_router
    print("SUCCESS: Routes imported")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
