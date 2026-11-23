# 🔥 FIREBOX — THE NEXT-GENERATION AI CODING AGENT

```
  ███████╗██╗██████╗ ███████╗██████╗  ██████╗ ██╗  ██╗
  ██╔════╝██║██╔══██╗██╔════╝██╔══██╗██╔══██╗╚██╗██╔╝
  █████╗  ██║██████╔╝█████╗  ██████╔╝██████╔╝ ╚███╔╝ 
  ██╔══╝  ██║██╔══██╗██╔══╝  ██╔══██╗██╔═══╝  ██╔██╗ 
  ██║     ██║██║  ██║███████╗██║  ██║██║     ██║  ██╗
  ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝
```

> **IGNITE YOUR CODE. BURN THROUGH TASKS.**

---

## 📖 What is FireBox?

**FireBox** is a high-performance, installable, cross-platform autonomous AI coding agent and developer platform. Inspired by the ergonomics of modern terminal coding assistants, FireBox is built from the ground up with its own architecture, fire-inspired terminal aesthetic, multi-provider engine, and deterministic safety mechanisms.

Unlike passive chat interfaces, FireBox operates as an active software engineer:
1. **Inspects your repository**: Understands project layout, languages, frameworks, and configuration files.
2. **Plans autonomously**: Formulates hierarchical milestone plans before executing changes.
3. **Executes real modifications**: Reads, creates, edits, and refactors files with surgical precision.
4. **Verifies through testing**: Runs tests and build commands to confirm that changes actually work.
5. **Self-heals and iterates**: Observes error traces, diagnoses the root cause, and auto-corrects.
6. **Protects your system**: Enforces workspace boundary confinement, maintains an append-only audit log, and creates automatic snapshots before mutations so you can rollback anytime with `/undo`.

---

## ⚡ Core Installation & Usage Commands

Here are the primary commands to install, launch, diagnose, and configure FireBox:

```powershell
# 1. Install FireBox (Automated Windows PowerShell Installer)
.\install.ps1

# 2. Or run portably without installation
.\bin\firebox.cmd

# 3. Start interactive TUI in current directory
firebox

# 4. Target a project directory
firebox .

# 5. Run diagnostics
firebox doctor

# 6. Run setup wizard
firebox setup
```

---

## 🚀 Step-by-Step Walkthrough

### 1. Automated Installation
Run the PowerShell installer to set up FireBox, create configuration directories, and register the global `firebox` executable command:
```powershell
.\install.ps1
```
*Note: If script execution is restricted on your system, run:*
```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

### 2. Portable Runner
Prefer not to install globally? FireBox includes standalone batch and PowerShell launchers ready to run out of the box:
```powershell
.\bin\firebox.cmd
# or in PowerShell
.\bin\firebox.ps1
```

### 3. Launching the Interactive TUI
To start the dark cinematic interface in your current working directory:
```bash
firebox
```
Or target any specific project folder:
```bash
firebox .
firebox C:\path\to\my-project
```

### 4. Running System Diagnostics (`firebox doctor`)
Validate that your environment, Python version, Git executable, storage permissions, and active AI model endpoints are fully operational:
```bash
firebox doctor
```

### 5. Running the Setup Wizard (`firebox setup`)
Easily configure your primary AI provider and API keys via the interactive wizard (select provider by **Number 1-19**), or via direct command-line flags. When typing or pasting your API key, it is visibly shown where you enter it with immediate registration card confirmation:
```bash
# Interactive setup wizard (prompts with numbered providers list 1-19)
firebox setup

# Choose provider by Number (e.g., #1 for OpenAI, #7 for Perplexity, #9 for SambaNova)
firebox setup -p 1 -k sk-proj-...
firebox setup -p 7 -k pplx-...
firebox setup -p 9 -k samba-...

# Or configure via provider add
firebox provider add 1 sk-proj-...
firebox provider add 7 pplx-...
```

---

## 🧪 Testing FireBox ("Test it OK")

FireBox includes a test suite covering the CLI, tools, safety permissions, providers, and agent loop:

```powershell
# Run the complete test suite (27+ tests)
python -m pytest tests/ -v
```

All automated tests pass:
- `tests/test_agent_engine.py`: Multi-turn loop, planning, modes, context, and sessions.
- `tests/test_cli.py`: CLI version, help, doctor, providers (numbered 1-19), setup by number, visible key registration, models, tools, permissions, analyze, and init.
- `tests/test_providers.py`: Provider registry, catalog resolution by number, model switching, mock simulator, Perplexity, Cohere, SambaNova, Qwen, and streaming.
- `tests/test_safety.py`: Workspace isolation, sensitive file protection, risk assessment, and rollback.
- `tests/test_tools.py`: File tools, search tools, project detection, and dependency inspection.

---

## 🛠️ Complete Feature Matrix

| Feature | Capabilities |
| :--- | :--- |
| **Terminal Aesthetics** | Modern OpenCode/Copilot-inspired minimal interface, subtle gray borders, blue navigation accents, orange Burner engine, syntax highlighting, diff viewer |
| **19 AI Providers (Numbered 1-19)** | OpenAI, Anthropic Claude 3.5/3.7, Google Gemini 2.0, DeepSeek V3/R1, Groq LPU, OpenRouter, **Perplexity AI**, **Cohere**, **SambaNova Systems**, **Alibaba Cloud Qwen**, Mistral, xAI, Together AI, Fireworks, Cerebras, NVIDIA NIM, Ollama, LM Studio, and offline Mock Simulator |
| **Visible API Key Input** | Secure yet transparent entry (`hide_input=False`) with immediate on-screen visual confirmation card displaying provider name, index, key, model, and secure storage status |
| **5 Agent Modes** | `ask` (read-only Q&A), `plan` (milestone roadmap), `build` (direct code generation), `autonomous` (self-healing loop), `review` (deep architectural audit) |
| **19 Built-in Tools** | `read_file`, `write_file`, `edit_file`, `list_dir`, `delete_file`, `file_search`, `text_search`, `code_symbol_search`, `shell_exec`, `run_tests`, `run_build`, `git_status`, `git_diff`, `git_commit`, `git_log`, `detect_project`, `inspect_dependencies`, `web_search`, `fetch_url` |
| **Safety & Confinement** | Workspace boundary enforcement, sensitive credential blacklist, pre-execution backups, `/undo` instant rollback, append-only audit trail |
| **Project Awareness** | Reads `FIREBOX.md`, `AGENTS.md`, `CLAUDE.md`, and `README.md` automatically for project-specific instructions |
| **Extensibility** | Dynamic Python plugin loading from `~/.firebox/plugins/` and Model Context Protocol (MCP) client support (`mcp.json`) |

---

## 🎮 Interactive Slash Commands (35+)

Inside the FireBox terminal interface, type `/` to access real-time autocomplete:

```
General:   /help  /doctor  /status  /clear  /settings  /exit
Sessions:  /new  /resume <id>  /sessions  /compact  /context
Providers: /providers  /provider <name>  /models  /model <name>
Workflow:  /plan <goal>  /execute  /approve  /reject  /undo  /retry
Coding:    /review  /test  /fix <issue>  /refactor <target>  /search <query>  /files  /diff  /git  /commit <msg>  /terminal <cmd>
```

### Keyboard Shortcuts
- **Ctrl+C**: Safely cancel current action or interrupt loop
- **Ctrl+L**: Clear terminal screen
- **Ctrl+P**: Quick model selector menu
- **Ctrl+O**: Open command menu
- **Ctrl+G**: Toggle plan view
- **Ctrl+T**: Toggle task info
- **Ctrl+D**: Exit FireBox

---

## 📚 Documentation Index

- [Installation Guide](file:///C:/Users/vivia/Downloads/FIREBOX/docs/INSTALLATION.md)
- [5-Minute Quickstart Tutorial](file:///C:/Users/vivia/Downloads/FIREBOX/docs/QUICKSTART.md)
- [AI Providers & Models Guide](file:///C:/Users/vivia/Downloads/FIREBOX/docs/PROVIDERS.md)
- [CLI Reference Guide](file:///C:/Users/vivia/Downloads/FIREBOX/docs/CLI_REFERENCE.md)
- [Slash Commands Reference](file:///C:/Users/vivia/Downloads/FIREBOX/docs/SLASH_COMMANDS.md)
- [Tool Registry & Custom Tools](file:///C:/Users/vivia/Downloads/FIREBOX/docs/TOOLS.md)
- [Plugins & MCP Architecture](file:///C:/Users/vivia/Downloads/FIREBOX/docs/PLUGINS_AND_MCP.md)
- [Security & Rollback Guide](file:///C:/Users/vivia/Downloads/FIREBOX/docs/SECURITY.md)
- [System Architecture](file:///C:/Users/vivia/Downloads/FIREBOX/docs/ARCHITECTURE.md)
- [Troubleshooting & Diagnostics](file:///C:/Users/vivia/Downloads/FIREBOX/docs/TROUBLESHOOTING.md)

---

## 📄 License
MIT License. Created by the FireBox AI Team.
