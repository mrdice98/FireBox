# FireBox Architecture & System Design

FireBox is engineered with a strict separation of concerns, ensuring high extensibility, testability, and deterministic safety.

```
                           ┌────────────────────────────┐
                           │      Terminal UI (TUI)     │
                           │  Rich + Prompt_Toolkit     │
                           └──────────────┬─────────────┘
                                          │
                                          ▼
                           ┌────────────────────────────┐
                           │      Agent Engine Loop     │
                           │ Observe ➔ Plan ➔ Act ➔ Test│
                           └───────┬────────────┬───────┘
                                   │            │
             ┌─────────────────────┘            └────────────────────┐
             ▼                                                       ▼
┌────────────────────────────┐                         ┌───────────────────────────┐
│     AI Provider Registry   │                         │       Tool Registry       │
│  (OpenAI, Claude, Gemini,  │                         │ File, Exec, Git, Search,  │
│   Ollama, DeepSeek, etc.)  │                         │ Project, Web, MCP Tools   │
└────────────┬───────────────┘                         └─────────────┬─────────────┘
             │                                                       │
             ▼                                                       ▼
┌────────────────────────────┐                         ┌───────────────────────────┐
│    Context & Memory        │                         │  Safety & Permission Gate │
│ Token limits, FIREBOX.md,  │                         │ Boundary confinement,     │
│ Session persistence        │                         │ Audit log, Rollback undo  │
└────────────────────────────┘                         └───────────────────────────┘
```

## Core Subsystems

### 1. Terminal UI Subsystem (`firebox.ui`)
- **Theme (`theme.py`)**: Centralizes the ember, flame orange, and dark charcoal palette.
- **Animations (`animations.py`)**: Renders the multi-frame animated particle logo reveal, status badges, and thinking spinners.
- **TUI (`tui.py`)**: Powers the interactive REPL with live command completion, multiline editing, history persistence, and custom keyboard bindings.
- **Diff Viewer (`diff_viewer.py`)**: Provides syntax-highlighted side-by-side or unified diff previews.

### 2. Provider Abstraction Layer (`firebox.providers`)
- **BaseProvider**: Standardizes chat completions, token streaming, tool call conversion, and reasoning content.
- **OpenAICompatibleProvider**: Powers OpenAI, DeepSeek, Groq, Mistral, xAI, OpenRouter, Together, Fireworks, Ollama, and LM Studio.
- **AnthropicProvider**: Implements Claude 3.5 & 3.7 Sonnet with extended thinking budget support.
- **GeminiProvider**: Supports Google Gemini 2.0 Flash, Gemini 2.0 Pro, and 1.5 Pro.
- **MockProvider**: Guarantees deterministic, 100% offline testing and demonstration without external API keys.

### 3. Safety & Permissions Subsystem (`firebox.safety`)
- **PermissionManager**: Restricts file modifications and executions strictly within the workspace root.
- **AuditLogger**: Writes immutable records of every operation to `~/.firebox/logs/audit.log`.
- **RollbackManager**: Captures file state before modification and enables instant restoration via `undo_last()`.

### 4. Agent Closed-Loop Engine (`firebox.agent`)
- Implements the multi-turn autonomous coding loop with strict iteration boundaries (`max_agent_iterations`).
- Automatically verifies changes by running tests or build scripts after file mutations.
