import requests

base = 'http://127.0.0.1:8000'
headers = {'Origin': 'http://127.0.0.1:8001'}
paths = ['/api/analytics/dashboard', '/api/camera/start', '/api/database/stats']

for p in paths:
    url = base + p
    try:
        if p.endswith('/start'):
            r = requests.post(url, json={'device_id': 0, 'frame_skip': 3, 'adaptive': True}, headers=headers, timeout=10)
        else:
            r = requests.get(url, headers=headers, timeout=10)
        print('==', p, '==')
        print('URL:', url)
        print('Status:', r.status_code)
        for k, v in r.headers.items():
            kl = k.lower()
            if 'access-control' in kl or kl in ('content-type',):
                print(f'{k}: {v}')
        try:
            print('JSON:', r.json())
        except Exception:
            print('TEXT:', r.text[:500])
    except Exception as e:
        print('ERROR calling', p, e)
