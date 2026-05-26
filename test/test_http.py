import urllib.request, json, os, time

api_key = os.environ.get('LITELLM_API_KEY', '')
body = json.dumps({
    "model": "fast",
    "messages": [{"role": "user", "content": "Say 'hello' in one word."}],
    "max_tokens": 10
}).encode()
req = urllib.request.Request(
    'http://litellm-gateway:4000/chat/completions',
    data=body,
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    },
    method='POST'
)
t0 = time.time()
try:
    resp = urllib.request.urlopen(req, timeout=120)
    elapsed = time.time() - t0
    data = json.loads(resp.read())
    content = data['choices'][0]['message']['content']
    print(f'OK ({elapsed:.1f}s): {content[:100]}')
except Exception as e:
    elapsed = time.time() - t0
    print(f'ERROR after {elapsed:.1f}s: {e}')
