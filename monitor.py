import urllib3
import json
import time
from urllib.parse import quote

http = urllib3.PoolManager()
token = '***REMOVED***'
allianceName = '***REMOVED***🍞'
webhookURL = '***REMOVED***'
interval = 900

while True:
    t = int(time.time())
    try:
        d = json.loads(http.request('GET', f'https://www.airline4.net/api/?access_token={token}&search={quote(allianceName)}').data.decode('utf-8'))
        if d['status']['request'] != 'success':
            raise ValueError()
        del d['status']
        with open(f'data/log/{allianceName}_{t}.json', 'w+', encoding='utf-8') as f:
            json.dump(d, f, indent=4)
        http.request('POST', webhookURL, body=json.dumps({'content': f'{t}: OK.'}), headers={'Content-Type': 'application/json'})
    except Exception:
        http.request('POST', webhookURL, body=json.dumps({'content': f'{t}: ERROR.'}), headers={'Content-Type': 'application/json'})
    time.sleep(interval)
