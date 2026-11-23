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

**FireBox** is an autonomous, cross-platform AI coding agent and developer platform built for developers who demand real results, speed, and safety. Powered by a closed-loop execution engine, 15+ AI providers, an extensible tool registry, and a cinematic terminal interface with fire-inspired visual aesthetics.

---

## ⚡ Key Highlights

- **Cinematic Dark Terminal UI**: Ember, flame, gold, and dark gradients, animated ASCII art logo reveal, live progress indicators, and syntax-highlighted diffs.
- **15+ AI Providers Supported**: OpenAI, Anthropic Claude 3.5/3.7, Google Gemini 2.0 Flash/Pro, OpenRouter, Groq, DeepSeek V3/R1, Mistral, xAI, Together AI, Fireworks, Cerebras, NVIDIA NIM, and local models via Ollama and LM Studio.
- **Real Agent Closed-Loop Architecture**: Observe → Plan → Select Tools → Execute → Observe → Verify → Iterate → Report.
- **19+ Built-in Tools**: File operations, unified diffing, code symbol search, regex text search, shell execution (PowerShell/Bash), Git operations, project stack detection, dependency analysis, and web research.
- **Rigorous Safety & Boundary Controls**: Workspace isolation, dangerous command blocking, operation risk assessment, audit logging, and instant file rollbacks (`undo_last`).
- **5 Execution Modes**: `ask` (read-only), `plan` (strategic breakdown), `build` (direct code generation), `autonomous` (full self-healing loop), and `review` (deep architectural audit).
- **Extensible Plugin & MCP System**: Dynamic plugin discovery and Model Context Protocol (MCP) client support to connect external tools.
- **Persistent Sessions**: Automatic session storage in JSON/Markdown with checkpoint resumption.

---

## 🚀 Quick Start

### Windows 10 / 11 Installation
Open Windows PowerShell and run:
```powershell
.\install.ps1
```

Or run portably from the repository:
```powershell
.\bin\firebox.cmd
```

### Launch FireBox
```bash
# Launch interactive cinematic TUI in current directory
firebox

# Target a specific project directory
firebox C:\path\to\my-project

# Run system health diagnostics
firebox doctor

# Run setup wizard
firebox setup
```

---

## 🎮 Interactive Slash Commands

Inside the interactive FireBox interface, type `/` to access instant command autocomplete:

| Command | Category | Description |
| :--- | :--- | :--- |
| `/help` | General | Display command reference and guide |
| `/doctor` | General | Run comprehensive system and provider diagnostics |
| `/status` | General | View workspace, model, provider, and mode status |
| `/clear` | General | Clear screen and redraw cinematic dashboard |
| `/new` | Session | Start a fresh session |
| `/resume <id>` | Session | Resume a saved session from disk |
| `/sessions` | Session | List all saved sessions |
| `/compact` | Session | Compact conversation context to preserve tokens |
| `/context` | Session | Inspect token usage and active instruction files |
| `/models` | Provider | List available models for active provider |
| `/model <name>` | Provider | Switch model on-the-fly (e.g. `/model claude-3-7-sonnet`) |
| `/providers` | Provider | List and inspect all 15+ supported AI providers |
| `/provider <id>` | Provider | Switch active provider (e.g. `/provider gemini`) |
| `/plan <goal>` | Workflow | Generate step-by-step milestone plan |
| `/review` | Coding | Perform architectural & security code review |
| `/test` | Coding | Run detected project tests (pytest, npm test, etc.) |
| `/fix <issue>` | Coding | Diagnose and repair test failures or bugs |
| `/diff` | Coding | Show workspace git diff |
| `/undo` | Safety | Revert the most recent file modification |
| `/exit` | General | Safely extinguish FireBox session |

---

## ⌨️ Keyboard Shortcuts

- **Ctrl+C**: Cancel the active operation safely.
- **Ctrl+L**: Clear terminal screen.
- **Ctrl+P**: Quick model selector menu.
- **Ctrl+O**: Open command menu.
- **Ctrl+G**: Toggle plan view.
- **Ctrl+T**: Toggle task information.
- **Ctrl+D**: Exit FireBox.

---

## 🛡️ Safety & Permission Levels

Configure safety via `firebox permissions` or in `~/.firebox/permissions.json`:
- **STRICT**: Prompts user for approval on all modifications and shell commands.
- **BALANCED** *(Default)*: Enforces workspace boundaries, blocks dangerous commands (`rm -rf /`, formatting drives), and prompts for destructive operations.
- **AUTONOMOUS**: Grants the agent autonomy to iterate, run tests, and fix errors within workspace boundaries.

---

## 📚 Documentation Index

- [Installation Guide](file:///C:/Users/vivia/Downloads/FIREBOX/docs/INSTALLATION.md)
- [Quickstart Tutorial](file:///C:/Users/vivia/Downloads/FIREBOX/docs/QUICKSTART.md)
- [AI Providers & Models Guide](file:///C:/Users/vivia/Downloads/FIREBOX/docs/PROVIDERS.md)
- [CLI Reference](file:///C:/Users/vivia/Downloads/FIREBOX/docs/CLI_REFERENCE.md)
- [Slash Commands Reference](file:///C:/Users/vivia/Downloads/FIREBOX/docs/SLASH_COMMANDS.md)
- [Tool Registry & Custom Tools](file:///C:/Users/vivia/Downloads/FIREBOX/docs/TOOLS.md)
- [Plugins and MCP Architecture](file:///C:/Users/vivia/Downloads/FIREBOX/docs/PLUGINS_AND_MCP.md)
- [Security & Rollback Guide](file:///C:/Users/vivia/Downloads/FIREBOX/docs/SECURITY.md)
- [System Architecture](file:///C:/Users/vivia/Downloads/FIREBOX/docs/ARCHITECTURE.md)
- [Troubleshooting & Diagnostics](file:///C:/Users/vivia/Downloads/FIREBOX/docs/TROUBLESHOOTING.md)

---

## 📄 License
MIT License. Created by the FireBox AI Team.
