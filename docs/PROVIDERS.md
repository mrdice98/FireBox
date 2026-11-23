# FireBox AI Providers & Models Guide

FireBox includes a modular provider architecture supporting **19 AI providers**, numbered 1 to 19 for instant selection, with visible API key input confirmation, local LLM runners, and custom OpenAI-compatible endpoints.

---

## Numbered Provider Catalog (1 - 19)

You can select any provider directly by its catalog number or ID in `firebox setup`, `firebox provider add`, or the interactive `/provider` slash command.

| # | Provider ID | Provider Name | Default Model | Key Required |
| :-: | :--- | :--- | :--- | :-: |
| **[ 1]** | `openai` | OpenAI | `gpt-4o` | Yes |
| **[ 2]** | `anthropic` | Anthropic | `claude-3-7-sonnet-20250219` | Yes |
| **[ 3]** | `gemini` | Google Gemini | `gemini-2.0-flash` | Yes |
| **[ 4]** | `deepseek` | DeepSeek | `deepseek-chat` | Yes |
| **[ 5]** | `groq` | Groq LPU | `llama-3.3-70b-versatile` | Yes |
| **[ 6]** | `openrouter` | OpenRouter | `anthropic/claude-3.7-sonnet` | Yes |
| **[ 7]** | `perplexity` | Perplexity AI *(New)* | `sonar-pro` | Yes |
| **[ 8]** | `cohere` | Cohere *(New)* | `command-r-plus` | Yes |
| **[ 9]** | `sambanova` | SambaNova Systems *(New)* | `Meta-Llama-3.3-70B-Instruct` | Yes |
| **[10]** | `qwen` | Alibaba Cloud Qwen *(New)* | `qwen-plus` | Yes |
| **[11]** | `mistral` | Mistral AI | `mistral-large-latest` | Yes |
| **[12]** | `xai` | xAI (Grok) | `grok-2-latest` | Yes |
| **[13]** | `together` | Together AI | `meta-llama/Llama-3.3-70B-Instruct-Turbo` | Yes |
| **[14]** | `fireworks` | Fireworks AI | `accounts/fireworks/models/llama-v3p3-70b-instruct` | Yes |
| **[15]** | `cerebras` | Cerebras | `llama3.1-70b` | Yes |
| **[16]** | `nvidia` | NVIDIA NIM | `meta/llama-3.3-70b-instruct` | Yes |
| **[17]** | `ollama` | Ollama (Local) | `llama3.1:latest` | No |
| **[18]** | `lmstudio` | LM Studio (Local)| `local-model` | No |
| **[19]** | `mock` | Mock Simulator | `firebox-sim-1.0` | No |

---

## Configuring Credentials & Visible Input

When plugging in an API key, FireBox displays the input visibly where you enter or paste it (`hide_input=False`), and immediately renders a verified **API Credential Registered** confirmation card showing the provider, exact key, model, and secure storage location.

### Option A: Interactive Setup Wizard
```bash
# Run wizard and choose provider by number (1-19)
firebox setup

# Or pass provider by number and key directly
firebox setup -p 1 -k sk-proj-...
firebox setup -p 7 -k pplx-...
firebox setup -p 9 -k samba-...
```

### Option B: Quick Provider Add
```bash
# Add key by provider number
firebox provider add 1 sk-proj-...
firebox provider add 7 pplx-...
firebox provider add 9 samba-...
```

### Option C: Environment Variables
```powershell
# Windows PowerShell
$env:OPENAI_API_KEY = "sk-..."
$env:ANTHROPIC_API_KEY = "sk-ant-..."
$env:GEMINI_API_KEY = "AIza..."
$env:PERPLEXITY_API_KEY = "pplx-..."
$env:COHERE_API_KEY = "..."
$env:SAMBANOVA_API_KEY = "..."
$env:DASHSCOPE_API_KEY = "..."
```

---

## Switching Models & Providers Inside the REPL

Inside the interactive FireBox REPL:
```bash
# List all providers with numbers
/providers

# Switch to OpenAI (Provider #1)
/provider 1

# Switch to Anthropic (Provider #2)
/provider 2

# Switch to Perplexity AI (Provider #7)
/provider 7

# Switch to SambaNova (Provider #9)
/provider 9

# Launch in-session setup / plug in API keys
/setup
/key

# Switch active model
/model claude-3-7-sonnet
/model sonar-pro
```

# Switch to Gemini 2.0 Flash
/provider gemini
/model gemini-2.0-flash

# Switch to Local Ollama
/provider ollama
/model llama3.1:latest
```
