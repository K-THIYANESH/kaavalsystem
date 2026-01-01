"""
KAAVAL System Diagnostic Script
Tests all components and provides clear status
"""
import requests
import json
from datetime import datetime

print("=" * 60)
print("KAAVAL SYSTEM DIAGNOSTIC")
print("=" * 60)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Test 1: Backend Health
print("[1/5] Testing Backend Connection...")
try:
    response = requests.get("http://localhost:8000/api/analytics/dashboard", timeout=5)
    if response.status_code == 200:
        print("✅ Backend API: WORKING")
        print(f"    Response: {response.json()}")
    else:
        print(f"❌ Backend API: Status {response.status_code}")
except Exception as e:
    print(f"❌ Backend API: FAILED - {e}")

# Test 2: CORS Headers
print("\n[2/5] Testing CORS Headers...")
try:
    response = requests.options(
        "http://localhost:8000/api/analytics/dashboard",
        headers={"Origin": "http://localhost:8001"},
        timeout=5
    )
    cors_headers = {
        "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin", "NOT SET"),
        "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods", "NOT SET"),
        "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers", "NOT SET"),
    }
    print("CORS Headers:")
    for key, value in cors_headers.items():
        status = "✅" if value != "NOT SET" else "❌"
        print(f"    {status} {key}: {value}")
except Exception as e:
    print(f"❌ CORS Test: FAILED - {e}")

# Test 3: All API Endpoints
print("\n[3/5] Testing API Endpoints...")
endpoints = [
    "/api/analytics/dashboard",
    "/api/camera/health",
    "/api/reports/missing/recent?limit=1",
]
for endpoint in endpoints:
    try:
        response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
        status = "✅" if response.status_code == 200 else "❌"
        print(f"    {status} {endpoint}: {response.status_code}")
    except Exception as e:
        print(f"    ❌ {endpoint}: {e}")

# Test 4: Frontend Accessibility
print("\n[4/5] Testing Frontend...")
try:
    response = requests.get("http://localhost:8001", timeout=5)
    if response.status_code == 200:
        print("✅ Frontend: ACCESSIBLE")
        print(f"    Content-Length: {len(response.content)} bytes")
    else:
        print(f"❌ Frontend: Status {response.status_code}")
except Exception as e:
    print(f"❌ Frontend: FAILED - {e}")

# Test 5: Summary
print("\n[5/5] Summary")
print("=" * 60)
print("\n📋 INSTRUCTIONS:")
print("1. If Backend API shows ✅ but CORS shows ❌:")
print("   → Backend needs restart to apply CORS fix")
print("   → Run: .\\start_project.ps1")
print("\n2. If all show ✅:")
print("   → Open http://localhost:8001")
print("   → Press Ctrl+Shift+R (hard refresh)")
print("   → Check browser console (F12)")
print("\n3. If errors persist:")
print("   → Share this diagnostic output")
print("   → Share browser console errors")
print("\n" + "=" * 60)
