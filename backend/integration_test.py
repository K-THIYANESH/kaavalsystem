#!/usr/bin/env python3
"""Test backend and frontend connectivity with CORS."""
import time
import requests
import json

print("=" * 60)
print("KAAVALCURSOR Backend & Frontend Integration Test")
print("=" * 60)

# Test 1: Backend Health
print("\n[Test 1] Backend Health Check")
try:
    r = requests.get('http://127.0.0.1:8000/healthz', timeout=5)
    print(f"✓ Status: {r.status_code}")
    print(f"✓ Response: {r.json()}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Frontend Static Assets
print("\n[Test 2] Frontend Static Assets")
try:
    r = requests.get('http://127.0.0.1:8001/index.html', timeout=5)
    print(f"✓ Status: {r.status_code}")
    print(f"✓ Content length: {len(r.text)} bytes")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: CORS Headers with Origin
print("\n[Test 3] CORS Response Headers (from frontend origin)")
origin_header = {'Origin': 'http://127.0.0.1:8001'}
try:
    r = requests.get('http://127.0.0.1:8000/healthz', headers=origin_header, timeout=5)
    print(f"✓ Status: {r.status_code}")
    cors_headers = {k: v for k, v in r.headers.items() if 'access-control' in k.lower()}
    if cors_headers:
        for k, v in cors_headers.items():
            print(f"  {k}: {v}")
    else:
        print("  (No explicit CORS headers returned)")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Analytics Dashboard
print("\n[Test 4] API: Analytics Dashboard")
try:
    r = requests.get('http://127.0.0.1:8000/api/analytics/dashboard', headers=origin_header, timeout=5)
    print(f"✓ Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"✓ Response keys: {list(data.keys())[:5]}...")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 5: Database Stats
print("\n[Test 5] API: Database Stats")
try:
    r = requests.get('http://127.0.0.1:8000/api/database/stats', headers=origin_header, timeout=5)
    print(f"✓ Status: {r.status_code}")
    if r.status_code == 200:
        print(f"✓ Response: {r.json()}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 6: Camera Start
print("\n[Test 6] API: Camera Start")
try:
    payload = {'device_id': 0, 'frame_skip': 3, 'adaptive': True}
    r = requests.post('http://127.0.0.1:8000/api/camera/start', json=payload, headers=origin_header, timeout=5)
    print(f"✓ Status: {r.status_code}")
    print(f"✓ Response: {r.json()}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
