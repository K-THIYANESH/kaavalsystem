import requests, time
for i in range(6):
    try:
        r = requests.get('http://127.0.0.1:8000/healthz', timeout=2)
        print('healthz ->', r.text)
        break
    except Exception as e:
        print('healthz attempt', i+1, 'failed:', e)
        time.sleep(1)
else:
    print('healthz unavailable')
