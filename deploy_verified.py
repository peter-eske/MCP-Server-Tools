#!/usr/bin/env python3
"""Löscht alle Modelle, die via Admin-API hinzugefügt wurden (nicht in Config),
und registriert nur die funktionierenden Modelle aus models_verified.json neu."""

import json
import os
import time
import urllib.request
import urllib.error
import ssl

LITELLM_URL = "http://localhost:4000"
MASTER_KEY = "sk-master-aRKrPNvkqJ78WTGLnUxgwluYMs9zS4pO"
VERIFIED = "models_verified.json"
DELAY = 0.2
ssl_ctx = ssl.create_default_context()

# Config-Modelle (NIEMALS löschen)
CONFIG_MODELS = {
    "claude-3-5-sonnet", "claude-3-5-haiku",
    "gpt-4o", "gpt-4o-mini", "gemini-2.5-flash",
    "deepseek-v4-flash", "qwen-3-coder-480b",
    "phi-4-mini", "llama-3.3-70b",
    "qwen-max", "qwen-plus", "qwen-turbo",
    "groq/llama-3.3-70b", "groq/llama-3.1-8b", "groq/deepseek-r1",
    "openrouter/claude-3.5-sonnet", "openrouter/gpt-4o", "openrouter/deepseek-v4",
    "together/llama-3.3-70b", "together/deepseek-v4", "together/qwen-3-coder",
    "cerebras/llama-3.3-70b",
    "huggingface/mistral-7b",
    "grok-2", "grok-3",
    "copilot/gpt-4o", "copilot/claude-3.5-sonnet",
    "airforce/gpt-4o", "airforce/claude-3.5-sonnet",
    "cf/llama-3.3-70b",
}

PROVIDER_CONFIG = {
    "Cerebras":     {"prefix": "openai/",  "api_base_field": True,  "api_base": "https://api.cerebras.ai/v1"},
    "Groq":         {"prefix": "groq/",    "api_base_field": False},
    "NVIDIA NIM":   {"prefix": "openai/",  "api_base_field": True,  "api_base": "https://integrate.api.nvidia.com/v1"},
    "OpenRouter":   {"prefix": "openai/",  "api_base_field": True,  "api_base": "https://openrouter.ai/api/v1"},
    "Together AI":  {"prefix": "together_ai/", "api_base_field": False},
}


def api(method, path, body=None):
    url = f"{LITELLM_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {MASTER_KEY}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl_ctx) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {"_error": e.read().decode()[:300]}


def main():
    if not os.path.exists(VERIFIED):
        print(f"FEHLER: {VERIFIED} nicht gefunden. Zuerst verify_models.py ausführen.")
        return

    with open(VERIFIED) as f:
        working = json.load(f)

    # ── Schritt 1: Alle API-Modelle löschen ──────────────────────────────
    print("Schritt 1: Vorhandene API-Modelle abrufen...")
    status, data = api("GET", "/model/info")
    if status != 200:
        print(f"  FEHLER: /model/info -> {status}")
        return

    all_db_models = data.get("data", [])
    to_delete = [m for m in all_db_models if m.get("model_name") not in CONFIG_MODELS]
    print(f"  {len(all_db_models)} Modelle gefunden, {len(to_delete)} API-Modelle zum Löschen")

    deleted = 0
    for m in to_delete:
        model_name = m["model_name"]
        status, _ = api("POST", "/model/delete", {"model_name": model_name})
        if status == 200:
            deleted += 1
        if deleted % 50 == 0:
            print(f"  Gelöscht: {deleted}/{len(to_delete)}")
        time.sleep(DELAY)

    print(f"  Gelöscht: {deleted} Modelle")

    # ── Schritt 2: Working-Modelle registrieren ──────────────────────────
    print(f"\nSchritt 2: {len(working)} Working-Modelle registrieren...")

    registered = 0
    for idx, m in enumerate(working):
        provider = m["provider"]
        pconf = PROVIDER_CONFIG.get(provider, {"prefix": "openai/", "api_base_field": True, "api_base": ""})

        model_name = m["model_id"].replace("/", "-").replace(".", "-").replace(":", "-")[:100]

        payload = {
            "model_name": model_name,
            "litellm_params": {
                "model": m["litellm_model"],
                "api_key": f"os.environ/{m['env_var']}",
            },
        }
        if pconf["api_base_field"] and pconf["api_base"]:
            payload["litellm_params"]["api_base"] = pconf["api_base"]

        status, result = api("POST", "/model/new", payload)
        if status == 200:
            registered += 1
        elif status == 400 and "exists" in str(result).lower():
            registered += 1
        else:
            print(f"  FEHLER [{model_name[:40]}]: {str(result.get('_error',''))[:100]}")

        if (idx + 1) % 20 == 0:
            print(f"  Fortschritt: {idx+1}/{len(working)} (OK: {registered})")
        time.sleep(DELAY)

    print(f"\n{'='*50}")
    print(f"Fertig: {registered} Working-Modelle registriert")
    print(f"(Config-Modelle ({len(CONFIG_MODELS)}) blieben unangetastet)")


if __name__ == "__main__":
    main()
