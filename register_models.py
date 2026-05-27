#!/usr/bin/env python3
"""Registriert alle Modelle aus models_catalog.json bei LiteLLM via Admin-API."""

import json
import os
import sys
import time
import urllib.request
import urllib.error
import ssl

LITELLM_URL = os.environ.get("LITELLM_URL", "http://localhost:4000")
MASTER_KEY = os.environ.get(
    "LITELLM_MASTER_KEY",
    "sk-master-aRKrPNvkqJ78WTGLnUxgwluYMs9zS4pO",
)
CATALOG = "models_catalog.json"
DELAY = 0.3  # seconds between requests
ssl_ctx = ssl.create_default_context()


# ── Provider-Gruppen: wie litellm_params.modell gebaut wird ───────────────
PROVIDER_CONFIG = {
    # Native Provider (litellm kennt das Prefix)
    "Anthropic":    {"prefix": "anthropic/",  "api_base_field": False},
    "Google Gemini":{"prefix": "gemini/",    "api_base_field": False},
    "Groq":         {"prefix": "groq/",     "api_base_field": False},
    "Together AI":  {"prefix": "together_ai/", "api_base_field": False},
    # OpenAI-kompatible Provider (brauchen api_base + openai/ Prefix)
    "OpenRouter":   {"prefix": "openai/",   "api_base_field": True},
    "NVIDIA NIM":   {"prefix": "openai/",   "api_base_field": True},
    "Cerebras":     {"prefix": "openai/",   "api_base_field": True},
    "API.Airforce": {"prefix": "openai/",   "api_base_field": True},
    "Cloudflare Workers AI": {"prefix": "openai/",  "api_base_field": True},
}


def call_api(method, path, body=None):
    url = f"{LITELLM_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {MASTER_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "register-models/1.0")
    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl_ctx) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {"_error": e.read().decode()}
    except Exception as e:
        return 0, {"_error": str(e)}


def main():
    if not os.path.exists(CATALOG):
        print(f"FEHLER: {CATALOG} nicht gefunden.")
        sys.exit(1)

    with open(CATALOG) as f:
        all_models = json.load(f)

    # deduplizieren nach litellm_model
    seen = set()
    unique = []
    for m in all_models:
        key = m["litellm_model"]
        if key not in seen:
            seen.add(key)
            unique.append(m)

    print(f"Zu registrieren: {len(unique)} Modelle (von {len(all_models)} mit Duplikaten)\n")

    stats = {"ok": 0, "skipped": 0, "errors": 0}

    for idx, m in enumerate(unique):
        provider = m["provider"]
        model_id = m["model_id"]
        litellm_model = m["litellm_model"]
        env_var = m["env_var"]
        api_base = m.get("api_base", "")

        pconf = PROVIDER_CONFIG.get(provider, {"prefix": "openai/", "api_base_field": True})

        # Modell-Namen aufbereiten (keine Sonderzeichen)
        model_name = model_id.replace("/", "-").replace(".", "-").replace(":", "-")
        model_name = model_name[:100]

        payload = {
            "model_name": model_name,
            "litellm_params": {
                "model": litellm_model,
                "api_key": f"os.environ/{env_var}",
            },
        }
        if pconf["api_base_field"] and api_base:
            payload["litellm_params"]["api_base"] = api_base

        status, result = call_api("POST", "/model/new", payload)
        if status == 200:
            stats["ok"] += 1
            status_str = "OK"
        elif status == 400 and "already exists" in str(result.get("_error", "")):
            stats["skipped"] += 1
            status_str = "EXISTS"
        else:
            stats["errors"] += 1
            status_str = f"ERR ({status})"
            err_msg = str(result.get("_error", ""))[:120]

        if idx % 20 == 0 or status != 200:
            print(f"[{idx+1}/{len(unique)}] {status_str} {provider:25s} {model_name[:50]:50s} {err_msg if status !=200 else ''}")

        time.sleep(DELAY)

    print(f"\n{'='*50}")
    print(f"Ergebnis: {stats['ok']} neu, {stats['skipped']} existieren, {stats['errors']} Fehler")


if __name__ == "__main__":
    main()
