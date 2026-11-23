# FireBox AI Providers & Models Guide

FireBox includes a provider abstraction layer supporting over 15 AI services, local LLM runners, and custom OpenAI-compatible endpoints.

---

## Supported Providers

| Provider ID | Provider Name | Default Model | Typical Endpoint |
| :--- | :--- | :--- | :--- |
| `openai` | OpenAI | `gpt-4o` | `https://api.openai.com/v1` |
| `anthropic` | Anthropic | `claude-3-7-sonnet` | `https://api.anthropic.com/v1` |
| `gemini` | Google Gemini | `gemini-2.0-flash` | `https://generativelanguage.googleapis.com` |
| `openrouter` | OpenRouter | `anthropic/claude-3.7-sonnet`| `https://openrouter.ai/api/v1` |
| `groq` | Groq | `llama-3.3-70b-versatile` | `https://api.groq.com/openai/v1` |
| `deepseek` | DeepSeek | `deepseek-chat` | `https://api.deepseek.com` |
| `mistral` | Mistral AI | `mistral-large-latest` | `https://api.mistral.ai/v1` |
| `xai` | xAI (Grok) | `grok-2-latest` | `https://api.x.ai/v1` |
| `together` | Together AI | `meta-llama/Llama-3.3-70B` | `https://api.together.xyz/v1` |
| `fireworks` | Fireworks AI | `llama-v3p3-70b-instruct` | `https://api.fireworks.ai/inference/v1` |
| `cerebras` | Cerebras | `llama3.1-70b` | `https://api.cerebras.ai/v1` |
| `nvidia` | NVIDIA NIM | `meta/llama-3.3-70b` | `https://integrate.api.nvidia.com/v1` |
| `ollama` | Ollama (Local) | `llama3.1:latest` | `http://localhost:11434/v1` |
| `lmstudio` | LM Studio (Local)| `local-model` | `http://localhost:1234/v1` |
| `mock` | Mock Simulator | `firebox-sim-1.0` | (Local offline emulator) |

---

## Configuring Credentials

You can supply API keys through environment variables or through the FireBox CLI.

### Option A: Environment Variables
```powershell
# Windows PowerShell
$env:OPENAI_API_KEY = "sk-..."
$env:ANTHROPIC_API_KEY = "sk-ant-..."
$env:GEMINI_API_KEY = "AIza..."
$env:DEEPSEEK_API_KEY = "sk-..."
$env:GROQ_API_KEY = "gsk_..."
```

### Option B: FireBox CLI
```bash
# Add key via command line
firebox provider add openai sk-...

# Or launch guided wizard
firebox setup
```

---

## Switching Models & Providers

Inside the interactive FireBox REPL:
```bash
# Switch to Claude 3.7 with Hybrid Reasoning
/provider anthropic
/model claude-3-7-sonnet

# Switch to Gemini 2.0 Flash
/provider gemini
/model gemini-2.0-flash

# Switch to Local Ollama
/provider ollama
/model llama3.1:latest
```
