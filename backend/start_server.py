"""
Simple startup script for KAAVAL backend server.
Run this with: python start_server.py
"""

import uvicorn

if __name__ == "__main__":
    print("="*60)
    print("  KAAVAL AI System - Starting Server")
    print("="*60)
    print("\nServer will start on: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server\n")
    print("="*60)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
