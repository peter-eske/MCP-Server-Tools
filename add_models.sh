#!/bin/bash
API="http://localhost:4000/model/new"
AUTH="Authorization: Bearer sk-master-aRKrPNvkqJ78WTGLnUxgwluYMs9zS4pO"

add() {
  echo "=== $1 ==="
  curl -s -X POST "$API" -H "$AUTH" -H "Content-Type: application/json" -d "$2" 2>&1 | head -c 200
  echo ""
}

# Anthropic
add "claude-3-5-sonnet" '{"model_name":"claude-3-5-sonnet","litellm_params":{"model":"anthropic/claude-3-5-sonnet-20241022","api_key":"os.environ/ANTHROPIC_API_KEY"}}'
add "claude-3-5-haiku" '{"model_name":"claude-3-5-haiku","litellm_params":{"model":"anthropic/claude-3-5-haiku-20241022","api_key":"os.environ/ANTHROPIC_API_KEY"}}'

# OpenAI
add "gpt-4o" '{"model_name":"gpt-4o","litellm_params":{"model":"openai/gpt-4o","api_key":"os.environ/OPENAI_API_KEY"}}'
add "gpt-4o-mini" '{"model_name":"gpt-4o-mini","litellm_params":{"model":"openai/gpt-4o-mini","api_key":"os.environ/OPENAI_API_KEY"}}'

# Gemini
add "gemini-2.5-flash" '{"model_name":"gemini-2.5-flash","litellm_params":{"model":"gemini/gemini-2.5-flash","api_key":"os.environ/GEMINI_API_KEY"}}'

# NVIDIA NIM
add "deepseek-v4-flash" '{"model_name":"deepseek-v4-flash","litellm_params":{"model":"openai/deepseek-ai/deepseek-v4-flash","api_base":"https://integrate.api.nvidia.com/v1","api_key":"os.environ/NVIDIA_API_KEY","max_tokens":8192,"temperature":0.2,"num_retries":0,"request_timeout":120}}'
add "qwen-3-coder-480b" '{"model_name":"qwen-3-coder-480b","litellm_params":{"model":"openai/qwen/qwen3-coder-480b-a35b-instruct","api_base":"https://integrate.api.nvidia.com/v1","api_key":"os.environ/NVIDIA_API_KEY","max_tokens":8192,"temperature":0.2,"num_retries":0,"request_timeout":300}}'
add "phi-4-mini" '{"model_name":"phi-4-mini","litellm_params":{"model":"openai/microsoft/phi-4-mini-instruct","api_base":"https://integrate.api.nvidia.com/v1","api_key":"os.environ/NVIDIA_API_KEY","max_tokens":2048,"temperature":0.5,"num_retries":0,"request_timeout":60}}'
add "llama-3.3-70b" '{"model_name":"llama-3.3-70b","litellm_params":{"model":"openai/meta/llama-3.3-70b-instruct","api_base":"https://integrate.api.nvidia.com/v1","api_key":"os.environ/NVIDIA_API_KEY","max_tokens":4096,"temperature":0.2,"num_retries":0,"request_timeout":180}}'

# Alibaba
add "qwen-max" '{"model_name":"qwen-max","litellm_params":{"model":"openai/qwen-max","api_base":"https://dashscope.aliyuncs.com/compatible-mode/v1","api_key":"os.environ/ALIBABA_API_KEY"}}'
add "qwen-plus" '{"model_name":"qwen-plus","litellm_params":{"model":"openai/qwen-plus","api_base":"https://dashscope.aliyuncs.com/compatible-mode/v1","api_key":"os.environ/ALIBABA_API_KEY"}}'
add "qwen-turbo" '{"model_name":"qwen-turbo","litellm_params":{"model":"openai/qwen-turbo","api_base":"https://dashscope.aliyuncs.com/compatible-mode/v1","api_key":"os.environ/ALIBABA_API_KEY"}}'

# Groq
add "groq/llama-3.3-70b" '{"model_name":"groq/llama-3.3-70b","litellm_params":{"model":"groq/llama-3.3-70b-versatile","api_key":"os.environ/GROQ_API_KEY"}}'
add "groq/llama-3.1-8b" '{"model_name":"groq/llama-3.1-8b","litellm_params":{"model":"groq/llama-3.1-8b-instant","api_key":"os.environ/GROQ_API_KEY"}}'
add "groq/deepseek-r1" '{"model_name":"groq/deepseek-r1","litellm_params":{"model":"groq/deepseek-r1-distill-llama-70b","api_key":"os.environ/GROQ_API_KEY"}}'

# OpenRouter
add "openrouter/claude-3.5-sonnet" '{"model_name":"openrouter/claude-3.5-sonnet","litellm_params":{"model":"openai/anthropic/claude-3.5-sonnet","api_base":"https://openrouter.ai/api/v1","api_key":"os.environ/OPENROUTER_API_KEY"}}'
add "openrouter/gpt-4o" '{"model_name":"openrouter/gpt-4o","litellm_params":{"model":"openai/openai/gpt-4o","api_base":"https://openrouter.ai/api/v1","api_key":"os.environ/OPENROUTER_API_KEY"}}'
add "openrouter/deepseek-v4" '{"model_name":"openrouter/deepseek-v4","litellm_params":{"model":"openai/deepseek/deepseek-chat","api_base":"https://openrouter.ai/api/v1","api_key":"os.environ/OPENROUTER_API_KEY"}}'

# Together AI
add "together/llama-3.3-70b" '{"model_name":"together/llama-3.3-70b","litellm_params":{"model":"together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo","api_key":"os.environ/TOGETHER_API_KEY"}}'
add "together/deepseek-v4" '{"model_name":"together/deepseek-v4","litellm_params":{"model":"together_ai/deepseek-ai/DeepSeek-V4","api_key":"os.environ/TOGETHER_API_KEY"}}'
add "together/qwen-3-coder" '{"model_name":"together/qwen-3-coder","litellm_params":{"model":"together_ai/Qwen/Qwen3-Coder-480B-A35B","api_key":"os.environ/TOGETHER_API_KEY"}}'

# Cerebras
add "cerebras/llama-3.3-70b" '{"model_name":"cerebras/llama-3.3-70b","litellm_params":{"model":"openai/meta-llama/Llama-3.3-70b","api_base":"https://api.cerebras.ai/v1","api_key":"os.environ/CEREBRAS_API_KEY"}}'

# HuggingFace
add "huggingface/mistral-7b" '{"model_name":"huggingface/mistral-7b","litellm_params":{"model":"huggingface/mistralai/Mistral-7B-Instruct-v0.3","api_key":"os.environ/HF_API_KEY"}}'

# xAI
add "grok-2" '{"model_name":"grok-2","litellm_params":{"model":"openai/grok-2","api_base":"https://api.x.ai/v1","api_key":"os.environ/XAI_API_KEY"}}'
add "grok-3" '{"model_name":"grok-3","litellm_params":{"model":"openai/grok-3","api_base":"https://api.x.ai/v1","api_key":"os.environ/XAI_API_KEY"}}'

# GitHub Copilot
add "copilot/gpt-4o" '{"model_name":"copilot/gpt-4o","litellm_params":{"model":"openai/gpt-4o","api_base":"https://api.githubcopilot.com","api_key":"os.environ/COPILOT_API_KEY"}}'
add "copilot/claude-3.5-sonnet" '{"model_name":"copilot/claude-3.5-sonnet","litellm_params":{"model":"openai/claude-3.5-sonnet","api_base":"https://api.githubcopilot.com","api_key":"os.environ/COPILOT_API_KEY"}}'

# api.airforce
add "airforce/gpt-4o" '{"model_name":"airforce/gpt-4o","litellm_params":{"model":"openai/gpt-4o","api_base":"https://api.airforce/v1","api_key":"os.environ/AIRFORCE_API_KEY"}}'
add "airforce/claude-3.5-sonnet" '{"model_name":"airforce/claude-3.5-sonnet","litellm_params":{"model":"openai/claude-3.5-sonnet","api_base":"https://api.airforce/v1","api_key":"os.environ/AIRFORCE_API_KEY"}}'

# Cloudflare
add "cf/llama-3.3-70b" '{"model_name":"cf/llama-3.3-70b","litellm_params":{"model":"openai/@cf/meta-llama/llama-3.3-70b-instruct","api_base":"https://api.cloudflare.com/client/v4/accounts/12fb04bba75c6666b35ac9678a60bc9d/ai/v1","api_key":"os.environ/CF_API_KEY"}}'

echo ""
echo "=== DONE ==="
