#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merged model_list YAML: Config-Modelle + Verified-Modelle (keine Dubletten)."""

import json
import unicodedata
from pathlib import Path

VERIFIED = Path(__file__).parent / "models_verified.json"

# ── Kuratierte Config-Modelle (bleiben erhalten, auch wenn verify nicht geht) ──
CURATED = [
    # ── ANTHROPIC ──
    {"model_name": "claude-3-5-sonnet",    "model": "anthropic/claude-3-5-sonnet-20241022",     "api_key": "os.environ/ANTHROPIC_API_KEY"},
    {"model_name": "claude-3-5-haiku",     "model": "anthropic/claude-3-5-haiku-20241022",      "api_key": "os.environ/ANTHROPIC_API_KEY"},
    # ── OPENAI ──
    {"model_name": "gpt-4o",               "model": "openai/gpt-4o",                            "api_key": "os.environ/OPENAI_API_KEY"},
    {"model_name": "gpt-4o-mini",          "model": "openai/gpt-4o-mini",                       "api_key": "os.environ/OPENAI_API_KEY"},
    # ── GEMINI ──
    {"model_name": "gemini-2.5-flash",     "model": "gemini/gemini-2.5-flash",                  "api_key": "os.environ/GEMINI_API_KEY"},
    # ── NVIDIA NIM (bestimmte) ──
    {"model_name": "deepseek-v4-flash",    "model": "openai/deepseek-ai/deepseek-v4-flash",     "api_key": "os.environ/NVIDIA_API_KEY",     "api_base": "https://integrate.api.nvidia.com/v1"},
    {"model_name": "qwen-3-coder-480b",    "model": "openai/qwen/qwen3-coder-480b-a35b-instruct","api_key": "os.environ/NVIDIA_API_KEY",    "api_base": "https://integrate.api.nvidia.com/v1"},
    {"model_name": "phi-4-mini",           "model": "openai/microsoft/phi-4-mini-instruct",     "api_key": "os.environ/NVIDIA_API_KEY",     "api_base": "https://integrate.api.nvidia.com/v1"},
    {"model_name": "llama-3.3-70b",        "model": "openai/meta/llama-3.3-70b-instruct",       "api_key": "os.environ/NVIDIA_API_KEY",     "api_base": "https://integrate.api.nvidia.com/v1"},
    # ── QWEN (Alibaba) ──
    {"model_name": "qwen-max",             "model": "openai/qwen-max",                          "api_key": "os.environ/ALIBABA_API_KEY",    "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
    {"model_name": "qwen-plus",            "model": "openai/qwen-plus",                         "api_key": "os.environ/ALIBABA_API_KEY",    "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
    {"model_name": "qwen-turbo",           "model": "openai/qwen-turbo",                        "api_key": "os.environ/ALIBABA_API_KEY",    "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
    # ── GROQ ──
    {"model_name": "groq/llama-3.3-70b",   "model": "groq/llama-3.3-70b-versatile",             "api_key": "os.environ/GROQ_API_KEY"},
    {"model_name": "groq/llama-3.1-8b",    "model": "groq/llama-3.1-8b-instant",                "api_key": "os.environ/GROQ_API_KEY"},
    {"model_name": "groq/deepseek-r1",     "model": "groq/deepseek-r1-distill-llama-70b",        "api_key": "os.environ/GROQ_API_KEY"},
    # ── OPENROUTER ──
    {"model_name": "openrouter/claude-3.5-sonnet",  "model": "openai/anthropic/claude-3.5-sonnet",      "api_key": "os.environ/OPENROUTER_API_KEY",  "api_base": "https://openrouter.ai/api/v1"},
    {"model_name": "openrouter/gpt-4o",             "model": "openai/openai/gpt-4o",                     "api_key": "os.environ/OPENROUTER_API_KEY",  "api_base": "https://openrouter.ai/api/v1"},
    {"model_name": "openrouter/deepseek-v4",        "model": "openai/deepseek/deepseek-chat",            "api_key": "os.environ/OPENROUTER_API_KEY",  "api_base": "https://openrouter.ai/api/v1"},
    # ── TOGETHER ──
    {"model_name": "together/llama-3.3-70b", "model": "together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo",  "api_key": "os.environ/TOGETHER_API_KEY"},
    {"model_name": "together/deepseek-v4",   "model": "together_ai/deepseek-ai/DeepSeek-V4",                  "api_key": "os.environ/TOGETHER_API_KEY"},
    {"model_name": "together/qwen-3-coder",  "model": "together_ai/Qwen/Qwen3-Coder-480B-A35B",              "api_key": "os.environ/TOGETHER_API_KEY"},
    # ── CEREBRAS ──
    {"model_name": "cerebras/llama-3.3-70b", "model": "openai/meta-llama/Llama-3.3-70b",     "api_key": "os.environ/CEREBRAS_API_KEY",  "api_base": "https://api.cerebras.ai/v1"},
    # ── HUGGINGFACE ──
    {"model_name": "huggingface/mistral-7b", "model": "huggingface/mistralai/Mistral-7B-Instruct-v0.3",  "api_key": "os.environ/HF_API_KEY"},
    # ── X.AI ──
    {"model_name": "grok-2",                "model": "openai/grok-2",             "api_key": "os.environ/XAI_API_KEY",   "api_base": "https://api.x.ai/v1"},
    {"model_name": "grok-3",                "model": "openai/grok-3",             "api_key": "os.environ/XAI_API_KEY",   "api_base": "https://api.x.ai/v1"},
    # ── GITHUB COPILOT ──
    {"model_name": "copilot/gpt-4o",       "model": "openai/gpt-4o",              "api_key": "os.environ/COPILOT_API_KEY",  "api_base": "https://api.githubcopilot.com"},
    {"model_name": "copilot/claude-3.5-sonnet", "model": "openai/claude-3.5-sonnet",  "api_key": "os.environ/COPILOT_API_KEY",  "api_base": "https://api.githubcopilot.com"},
    # ── API.AIRFORCE ──
    {"model_name": "airforce/gpt-4o",              "model": "openai/gpt-4o",           "api_key": "os.environ/AIRFORCE_API_KEY",  "api_base": "https://api.airforce/v1"},
    {"model_name": "airforce/claude-3.5-sonnet",   "model": "openai/claude-3.5-sonnet","api_key": "os.environ/AIRFORCE_API_KEY",  "api_base": "https://api.airforce/v1"},
    # ── CLOUDFLARE ──
    {"model_name": "cf/llama-3.3-70b", "model": "openai/@cf/meta-llama/llama-3.3-70b-instruct",  "api_key": "os.environ/CF_API_KEY",  "api_base": "https://api.cloudflare.com/client/v4/accounts/12fb04bba75c6666b35ac9678a60bc9d/ai/v1"},
]

# Verified-Modelle bauen eigene model_name-Menge für Dedup
VERIFIED_MODEL_NAMES = set()

def sanitize(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return s.replace("/", "-").replace(":", "-")[:100]

def gen_yaml_entry(entry):
    lines = []
    lines.append(f'  - model_name: {entry["model_name"]}')
    lines.append(f'    litellm_params:')
    lines.append(f'      model: {entry["model"]}')
    lines.append(f'      api_key: {entry["api_key"]}')
    if entry.get("api_base"):
        lines.append(f'      api_base: {entry["api_base"]}')
    lines.append("")
    return "\n".join(lines)


def main():
    all_entries = []

    # 1. Curated Models zuerst
    for e in CURATED:
        all_entries.append(("Curated", e["model_name"], gen_yaml_entry(e)))

    # 2. Verified Models dazu (falls nicht schon curated)
    with open(VERIFIED, encoding="utf-8") as f:
        verified = json.load(f)

    PROVIDER_CONFIG = {
        "Cerebras":     {"api_base": "https://api.cerebras.ai/v1"},
        "NVIDIA NIM":   {"api_base": "https://integrate.api.nvidia.com/v1"},
        "OpenRouter":   {"api_base": "https://openrouter.ai/api/v1"},
    }

    curated_names = {e["model_name"] for e in CURATED}

    for m in sorted(verified, key=lambda x: (x["provider"], x["model_id"])):
        provider = m["provider"]
        pconf = PROVIDER_CONFIG.get(provider, {})
        model_name = sanitize(m["model_id"])

        if model_name in curated_names:
            continue

        entry = {
            "model_name": model_name,
            "model": m["litellm_model"],
            "api_key": f"os.environ/{m['env_var']}",
        }
        if pconf.get("api_base"):
            entry["api_base"] = pconf["api_base"]

        all_entries.append(("Verified", model_name, gen_yaml_entry(entry)))

    # Ausgabe
    header = """  # ── MODEL LIST (Curated + Verified) ──────────────────────────"""

    body_lines = [header]
    for source, name, yaml in all_entries:
        body_lines.append(yaml)

    out_path = Path(__file__).parent / "model_list_merged.yaml"
    output = "\n".join(body_lines)
    out_path.write_text(output, encoding="utf-8")

    curated_count = sum(1 for s, _, _ in all_entries if s == "Curated")
    verified_count = sum(1 for s, _, _ in all_entries if s == "Verified")
    print(f"Generiert: {out_path}")
    print(f"  Curated:  {curated_count}")
    print(f"  Verified: {verified_count}")
    print(f"  Gesamt:   {curated_count + verified_count}")

if __name__ == "__main__":
    main()
