# CHANGELOG

## [1.0.0] — 2026-11-23 — "Prometheus Ember"

### Initial Release Highlights

- **Cinematic Terminal User Interface (TUI)**:
  - Custom ember, flame orange, gold, and dark charcoal theme.
  - Multi-frame animated fire sparkle and ASCII logo reveal.
  - Rich syntax-highlighted code panels and interactive unified diff viewer.
  - Full keyboard shortcuts (`Ctrl+C`, `Ctrl+L`, `Ctrl+P`, `Ctrl+O`, `Ctrl+G`, `Ctrl+T`, `Ctrl+D`).
- **AI Provider Engine**:
  - Unified multi-provider abstraction supporting 15+ backends: OpenAI, Anthropic, Google Gemini, OpenRouter, Groq, DeepSeek, Mistral, xAI, Together AI, Fireworks, Cerebras, NVIDIA NIM, Ollama, LM Studio, and offline mock simulator.
  - Extended reasoning token capture (Claude 3.7 Sonnet, DeepSeek R1, OpenAI o1/o3-mini).
- **Autonomous Agent Loop**:
  - Closed-loop observe-plan-act-verify-iterate engine.
  - 5 operational modes: `ask`, `plan`, `build`, `autonomous`, and `review`.
  - Context compression and project instructions (`FIREBOX.md`, `AGENTS.md`, `CLAUDE.md`).
- **Modular Tool Registry**:
  - 19 core tools covering files, regex grep, AST symbols, shell execution, Git, project detection, and web search.
- **Security & Rollback**:
  - Workspace boundary confinement.
  - Pre-execution snapshots and one-click rollback (`undo_last`).
  - Append-only audit logger.
- **Packaging & Delivery**:
  - Windows PowerShell installer (`install.ps1`).
  - Standalone portable launcher (`bin/firebox.cmd`, `bin/firebox.ps1`).
  - Linux/macOS installer (`install.sh`).
  - Portable zip bundle builder (`package.py`).
