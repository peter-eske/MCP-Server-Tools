#!/usr/bin/env python3
"""Testet alle Modelle aus models_catalog.json gegen die echten Anbieter-APIs.
Speichert models_verified.json mit Status und Modell-Infos."""

import json
import os
import time
import ssl
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

INPUT = Path(__file__).parent / "models_catalog.json"
OUTPUT = Path(__file__).parent / "models_verified.json"
TIMEOUT = 15
MAX_WORKERS = 15
ssl_ctx = ssl.create_default_context()

# ── Provider-Konfiguration für API-Calls ──────────────────────────────────
PROVIDER_API = {
    "Anthropic": {
        "url": lambda m: "https://api.anthropic.com/v1/messages",
        "headers": lambda key: {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        "body": lambda m: {
            "model": m["model_id"],
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "Hi"}],
        },
        "success_check": lambda d: "content" in d,
    },
    "Google Gemini": {
        "url": lambda m: f"https://generativelanguage.googleapis.com/v1beta/models/{m['model_id']}:generateContent?key={m['api_key']}",
        "headers": lambda key: {"Content-Type": "application/json"},
        "body": lambda m: {"contents": [{"parts": [{"text": "Hi"}]}], "generationConfig": {"maxOutputTokens": 1}},
        "success_check": lambda d: "candidates" in d,
    },
    "Groq": {
        "url": lambda m: "https://api.groq.com/openai/v1/chat/completions",
        "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        "body": lambda m: {"model": m["model_id"], "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 1},
        "success_check": lambda d: "choices" in d,
    },
    "OpenRouter": {
        "url": lambda m: "https://openrouter.ai/api/v1/chat/completions",
        "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        "body": lambda m: {"model": m["model_id"], "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 1},
        "success_check": lambda d: "choices" in d,
    },
    "Together AI": {
        "url": lambda m: "https://api.together.xyz/v1/chat/completions",
        "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        "body": lambda m: {"model": m["model_id"], "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 1},
        "success_check": lambda d: "choices" in d,
    },
    "Cerebras": {
        "url": lambda m: "https://api.cerebras.ai/v1/chat/completions",
        "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        "body": lambda m: {"model": m["model_id"], "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 1},
        "success_check": lambda d: "choices" in d,
    },
    "NVIDIA NIM": {
        "url": lambda m: "https://integrate.api.nvidia.com/v1/chat/completions",
        "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        "body": lambda m: {"model": m["model_id"], "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 1},
        "success_check": lambda d: "choices" in d,
    },
    "API.Airforce": {
        "url": lambda m: "https://api.airforce/v1/chat/completions",
        "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        "body": lambda m: {"model": m["model_id"], "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 1},
        "success_check": lambda d: "choices" in d,
    },
    "Cloudflare Workers AI": {
        "url": lambda m: f"https://api.cloudflare.com/client/v4/accounts/12fb04bba75c6666b35ac9678a60bc9d/ai/run/{m['model_id']}",
        "headers": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        "body": lambda m: {"messages": [{"role": "user", "content": "Hi"}], "max_tokens": 1},
        "success_check": lambda d: d.get("success") is True or "result" in d,
    },
}

# Modelle, bei denen die API-Key-Formate nicht mit dem Test-Endpunkt kompatibel sind
SKIP_PROVIDERS = {"OpenAI": "Key nicht kompatibel", "X.AI (Grok)": "403 Forbidden", "Alibaba Cloud (Tongyi Qwen)": "401 Unauthorized", "GitHub Copilot": "Kein Test-Endpunkt"}

def resolve_api_key(m):
    """Key aus models_catalog.json oder aus der lokalen Umgebung."""
    env_var = m.get("env_var", "")
    key = os.environ.get(env_var, "")
    return key

def test_model(m):
    """Testet ein einzelnes Modell. Returns (model_dict, status)."""
    provider = m["provider"]

    if provider in SKIP_PROVIDERS:
        m["verified"] = "skip"
        m["skip_reason"] = SKIP_PROVIDERS[provider]
        return m

    pconf = PROVIDER_API.get(provider)
    if not pconf:
        m["verified"] = "skip"
        m["skip_reason"] = f"Keine Test-Konfiguration für {provider}"
        return m

    api_key = resolve_api_key(m)
    if not api_key:
        # Fallback: Hardcoded keys aus der models_catalog (wurden beim Fetch verwendet)
        meta = FETCH_KEYS.get(provider, "")
        if meta:
            api_key = meta
        else:
            m["verified"] = "skip"
            m["skip_reason"] = "Kein API-Key verfügbar"
            return m

    url = pconf["url"](m)
    headers = pconf["headers"](api_key)
    body = pconf["body"](m)
    data = json.dumps(body).encode()

    req = urllib.request.Request(url, data=data, method="POST")
    for k, v in headers.items():
        req.add_header(k, v)
    req.add_header("User-Agent", "MCP-Verify/1.0")

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ssl_ctx) as resp:
            resp_data = json.loads(resp.read().decode())
            duration = round(time.time() - start, 2)
            if pconf["success_check"](resp_data):
                m["verified"] = "ok"
                m["duration"] = duration
            else:
                m["verified"] = "fail"
                m["error"] = f"Unerwartete Antwort: {str(resp_data)[:200]}"
                m["duration"] = duration
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()[:200]
        m["verified"] = "fail"
        m["error"] = f"HTTP {e.code}: {err_body}"
    except urllib.error.URLError as e:
        m["verified"] = "fail"
        m["error"] = f"URL Error: {e.reason}"
    except json.JSONDecodeError as e:
        m["verified"] = "fail"
        m["error"] = f"JSON Error: {e}"
    except Exception as e:
        m["verified"] = "fail"
        m["error"] = f"{type(e).__name__}: {e}"

    return m


FETCH_KEYS = {
    "Anthropic": os.environ.get("ANTHROPIC_API_KEY", ""),
    "Google Gemini": os.environ.get("GEMINI_API_KEY", ""),
    "Groq": os.environ.get("GROQ_API_KEY", ""),
    "OpenRouter": os.environ.get("OPENROUTER_API_KEY", ""),
    "Together AI": os.environ.get("TOGETHER_API_KEY", ""),
    "Cerebras": os.environ.get("CEREBRAS_API_KEY", ""),
    "NVIDIA NIM": os.environ.get("NVIDIA_API_KEY", ""),
    "API.Airforce": os.environ.get("AIRFORCE_API_KEY", ""),
    "Cloudflare Workers AI": os.environ.get("CF_API_KEY", ""),
}


def main():
    if not INPUT.exists():
        print(f"FEHLER: {INPUT} nicht gefunden. Zuerst fetch_models.py ausführen.")
        return

    with open(INPUT) as f:
        catalog = json.load(f)

    print(f"Teste {len(catalog)} Modelle ({MAX_WORKERS} parallel, {TIMEOUT}s Timeout)...\n")

    results = []
    done = 0
    start_all = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(test_model, m): m for m in catalog}
        for future in as_completed(futures):
            m = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                m["verified"] = "error"
                m["error"] = str(e)
                results.append(m)

            done += 1
            if done % 25 == 0 or done == len(catalog):
                elapsed = time.time() - start_all
                ok_now = sum(1 for r in results if r.get("verified") == "ok")
                fail_now = sum(1 for r in results if r.get("verified", "").startswith("fail"))
                skip_now = sum(1 for r in results if r.get("verified") == "skip")
                print(f"  [{done}/{len(catalog)}] {elapsed:.0f}s | OK:{ok_now} FAIL:{fail_now} SKIP:{skip_now}")

    elapsed = time.time() - start_all
    ok = sum(1 for r in results if r.get("verified") == "ok")
    fail = sum(1 for r in results if r.get("verified", "").startswith("fail"))
    skip = sum(1 for r in results if r.get("verified") == "skip")
    error = sum(1 for r in results if r.get("verified") == "error")

    # Nur OK-Modelle in den verified-Katalog
    verified = [r for r in results if r.get("verified") == "ok"]

    OUTPUT.write_text(json.dumps(verified, indent=2, ensure_ascii=False))

    print(f"\n{'='*55}")
    print(f"Fertig in {elapsed:.0f}s")
    print(f"  OK:    {ok}")
    print(f"  FAIL:  {fail}")
    print(f"  SKIP:  {skip}")
    print(f"  ERROR: {error}")
    print(f"  → {len(verified)} funktionierende Modelle gespeichert in {OUTPUT}")

    # Zusammenfassung pro Provider
    print(f"\n  Nach Provider:")
    providers = {}
    for r in results:
        p = r["provider"]
        if p not in providers:
            providers[p] = {"ok": 0, "fail": 0, "skip": 0}
        providers[p][r.get("verified", "error") if not r.get("verified", "").startswith("fail") else "fail"] += 1
    for p, s in sorted(providers.items()):
        print(f"    {p:25s} OK:{s['ok']:4d} FAIL:{s['fail']:4d} SKIP:{s['skip']:4d}")

    # Auch Rohdaten speichern (alle mit Status)
    raw_output = Path(__file__).parent / "models_verified_raw.json"
    raw_output.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\n  Rohdaten: {raw_output}")


if __name__ == "__main__":
    main()
