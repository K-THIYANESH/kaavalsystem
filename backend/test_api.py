# Test Backend API Connectivity
import requests
import json

print("Testing KAAVAL Backend API...")
print("=" * 50)

# Test 1: Analytics Dashboard
try:
    response = requests.get("http://localhost:8000/api/analytics/dashboard", timeout=5)
    print(f"\n✅ Analytics API: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"\n❌ Analytics API Failed: {e}")

# Test 2: Health Check
try:
    response = requests.get("http://localhost:8000/api/camera/health", timeout=5)
    print(f"\n✅ Camera Health API: {response.status_code}")
except Exception as e:
    print(f"\n❌ Camera Health API Failed: {e}")

# Test 3: Reports
try:
    response = requests.get("http://localhost:8000/api/reports/missing/recent?limit=5", timeout=5)
    print(f"\n✅ Reports API: {response.status_code}")
except Exception as e:
    print(f"\n❌ Reports API Failed: {e}")

print("\n" + "=" * 50)
print("Backend API Test Complete")
