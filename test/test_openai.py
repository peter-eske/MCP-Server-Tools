import os, openai, time

api_key = os.environ.get("LITELLM_API_KEY", "")

t0 = time.time()
try:
    client = openai.OpenAI(base_url="http://litellm-gateway:4000", api_key=api_key)
    resp = client.chat.completions.create(model="default", messages=[{"role": "user", "content": "Say hello in one word"}], max_tokens=10)
    print(f"OK ({time.time()-t0:.1f}s): {resp.choices[0].message.content}")
except Exception as e:
    print(f"ERROR ({time.time()-t0:.1f}s): {type(e).__name__}: {e}")
