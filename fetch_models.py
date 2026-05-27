#!/usr/bin/env python3
"""Ruft alle verfuegbaren Modelle von allen Providern ab und speichert sie als JSON."""

import json
import os
import time
import urllib.request
import urllib.error
import ssl
from pathlib import Path

OUTPUT = Path(__file__).parent / "models_catalog.json"
TIMEOUT = 30
ssl_ctx = ssl.create_default_context()

def req(url, headers, retries=2):
    for i in range(retries):
        try:
            r = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(r, timeout=TIMEOUT, context=ssl_ctx) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            if i < retries - 1:
                time.sleep(2)
                continue
            return {"_error": str(e)}

# ── Provider-Definitionen ─────────────────────────────────────────────────
PROVIDERS = [
    {
        "name": "Anthropic",
        "base_url": "https://api.anthropic.com/v1/models",
        "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
        "headers": {"x-api-key": os.environ.get("ANTHROPIC_API_KEY", ""), "anthropic-version": "2023-06-01"},
        "parser": lambda j: [{"id": m["id"], "litellm": f"anthropic/{m['id']}"} for m in j.get("data", [])],
    },
    {
        "name": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1/models",
        "api_key": os.environ.get("GEMINI_API_KEY", ""),
        "parser": lambda j: [{"id": m["name"].replace("models/", ""), "litellm": f"gemini/{m['name'].replace('models/', '')}"} for m in j.get("models", [])],
    },
    {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1/models",
        "api_key": os.environ.get("OPENAI_API_KEY", ""),
        "parser": lambda j: [{"id": m["id"], "litellm": f"openai/{m['id']}"} for m in j.get("data", [])],
    },
    {
        "name": "Groq",
        "base_url": "https://api.groq.com/openai/v1/models",
        "api_key": os.environ.get("GROQ_API_KEY", ""),
        "parser": lambda j: [{"id": m["id"], "litellm": f"groq/{m['id']}"} for m in j.get("data", [])],
    },
    {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1/models",
        "api_key": os.environ.get("OPENROUTER_API_KEY", ""),
        "parser": lambda j: [{"id": m["id"], "litellm": f"openai/{m['id']}"} for m in j.get("data", [])],
    },
    {
        "name": "Together AI",
        "base_url": "https://api.together.xyz/v1/models",
        "api_key": os.environ.get("TOGETHER_API_KEY", ""),
        "parser": lambda j: [{"id": m["id"], "litellm": f"together_ai/{m['id']}"} for m in j],
    },
    {
        "name": "Cerebras",
        "base_url": "https://api.cerebras.ai/v1/models",
        "api_key": os.environ.get("CEREBRAS_API_KEY", ""),
        "parser": lambda j: [{"id": m["id"], "litellm": f"openai/{m['id']}"} for m in j],
    },
    {
        "name": "X.AI (Grok)",
        "base_url": "https://api.x.ai/v1/models",
        "api_key": os.environ.get("XAI_API_KEY", ""),
        "parser": lambda j: [{"id": m["id"], "litellm": f"openai/{m['id']}"} for m in j],
    },
    {
        "name": "NVIDIA NIM",
        "base_url": "https://integrate.api.nvidia.com/v1/models",
        "api_key": os.environ.get("NVIDIA_API_KEY", ""),
        "headers": lambda: _nvidia_headers(),
        "parser": lambda j: [{"id": m["id"], "litellm": f"openai/{m['id']}"} for m in j],
    },
    {
        "name": "Alibaba (Qwen)",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/models",
        "api_key": os.environ.get("ALIBABA_API_KEY", ""),
        "parser": lambda j: [{"id": m["id"], "litellm": f"openai/{m['id']}"} for m in j.get("data", [])],
    },
    {
        "name": "API.Airforce",
        "base_url": "https://api.airforce/v1/models",
        "api_key": os.environ.get("AIRFORCE_API_KEY", ""),
        "parser": lambda j: [{"id": m["id"], "litellm": f"openai/{m['id']}"} for m in j],
    },
    {
        "name": "Cloudflare Workers AI",
        "base_url": "https://api.cloudflare.com/client/v4/accounts/12fb04bba75c6666b35ac9678a60bc9d/ai/",
        "api_key": os.environ.get("CF_API_KEY", ""),
        "parser": lambda j: [{"id": m["id"], "litellm": f"openai/@cf/{m['id']}"} for m in j.get("result", [])],
    },
    {
        "name": "GitHub (Copilot)",
        "base_url": "https://api.githubcopilot.com/models",
        "api_key": os.environ.get("COPILOT_API_KEY", ""),
        "parser": lambda j: [{"id": m["id"], "litellm": f"openai/{m['id']}"} for m in j.get("data", [])],
    },
    {
        "name": "HuggingFace",
        "base_url": "https://api-inference.huggingface.co/models?pipeline_tag=text-generation&sort=downloads&limit=100",
        "api_key": os.environ.get("HF_API_KEY", ""),
        "parser": lambda j: [{"id": m["id"], "litellm": f"huggingface/{m['id']}"} for m in j],
    },
]


def fetch_all():
    catalog = []
    errors = []

    for p in PROVIDERS:
        name = p["name"]
        print(f"[{name}] Abrufen von {p['list_url']} ...", end=" ")

        headers = {"User-Agent": "MCP-Server-Tools/1.0"}

        if p.get("no_bearer"):
            pass  # key already in URL or no auth header needed
        elif p.get("auth_header") == "Authorization":
            headers["Authorization"] = f"Bearer {p['api_key']}"
        elif name == "Anthropic":
            headers["x-api-key"] = p["api_key"]
        else:
            headers["Authorization"] = f"Bearer {p['api_key']}"
        headers.update(p.get("headers_extra") or {})

        data = req(p["list_url"], headers)
        if "_error" in data:
            print(f"FEHLER: {data['_error']}")
            errors.append({"provider": name, "error": data["_error"]})
            continue

        raw = data
        rk = p["response_data_key"]
        if rk:
            raw = data.get(rk, data)

        if not isinstance(raw, list):
            print(f"unerwartetes Format: {type(raw).__name__}")
            errors.append({"provider": name, "error": f"unerwartetes Format: {type(raw).__name__}"})
            continue

        id_key = p["id_key"]
        filt = p.get("filter")
        id_transform = p.get("id_transform", lambda v: v)
        litellm_prefix = p["litellm_prefix"]
        api_base = p.get("api_base", "")

        count = 0
        for item in raw:
            if not isinstance(item, dict):
                continue
            raw_id = item.get(id_key, "")
            if not raw_id:
                continue
            model_id = id_transform(raw_id)
            if filt and not filt(item):
                continue
            # skip embedding-only models
            owned = item.get("owned_by", "")
            if "embed" in model_id.lower() or "embed" in owned.lower():
                continue
            entry = {
                "provider": name,
                "env_var": p["env_var"],
                "model_id": model_id,
                "litellm_model": f"{litellm_prefix}{model_id}",
                "api_base": api_base,
            }
            catalog.append(entry)
            count += 1

        print(f"{count} Modelle")

    print(f"\n{'='*50}")
    print(f"Gesamt: {len(catalog)} Modelle von {len(PROVIDERS)} Providern")
    if errors:
        print(f"Fehler: {len(errors)}")
        for e in errors:
            print(f"  - {e['provider']}: {e['error']}")

    catalog.sort(key=lambda x: (x["provider"], x["model_id"]))

    # limit OpenRouter to ~300 to avoid explosion
    or_count = sum(1 for c in catalog if c["provider"] == "OpenRouter")
    if or_count > 300:
        keep = []
        dropped = 0
        for c in catalog:
            if c["provider"] == "OpenRouter":
                dropped += 1
                if dropped <= 300:
                    keep.append(c)
            else:
                keep.append(c)
        catalog = keep
        print(f"OpenRouter auf 300 Modelle begrenzt ({dropped} verworfen)")

    OUTPUT.write_text(json.dumps(catalog, indent=2, ensure_ascii=False))
    print(f"\nGespeichert: {OUTPUT}")
    return catalog


if __name__ == "__main__":
    fetch_all()
