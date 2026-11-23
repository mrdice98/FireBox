# FireBox Slash Commands Reference

FireBox provides over 35 interactive slash commands within the terminal UI. Type `/` in the prompt to trigger interactive auto-completion.

---

## General Commands

| Command | Description |
| :--- | :--- |
| `/help` | Display the interactive command reference card. |
| `/doctor` | Run comprehensive system, provider, and tool diagnostics. |
| `/status` | View current workspace, active model, provider, and mode. |
| `/clear` | Clear the terminal and redraw the dashboard. |
| `/settings` | Inspect global configuration and animation preferences. |
| `/exit`, `/quit` | Safely close the FireBox session. |

---

## Session Commands

| Command | Description |
| :--- | :--- |
| `/new` | Initialize a clean new conversation session. |
| `/resume <id>` | Resume a previous session from history. |
| `/sessions` | List all saved conversation sessions with metadata. |
| `/compact` | Compact conversation history to reduce token consumption. |
| `/context` | Display current token count and active instruction files. |

---

## Provider & Model Commands

| Command | Description |
| :--- | :--- |
| `/providers` | List all 15+ supported AI providers and their configuration status. |
| `/provider <name>` | Switch active AI provider (e.g. `/provider gemini`). |
| `/models` | List available models for the current active provider. |
| `/model <id>` | Switch the active model (e.g. `/model claude-3-7-sonnet`). |

---

## Coding & Workflow Commands

| Command | Description |
| :--- | :--- |
| `/plan <goal>` | Formulate a structured step-by-step milestone plan. |
| `/execute` | Execute pending steps in the active plan. |
| `/review` | Perform a deep code review of modified files. |
| `/test` | Automatically detect and run project tests. |
| `/fix <issue>` | Auto-diagnose errors and implement verified fixes. |
| `/refactor <target>` | Refactor code for readability and performance. |
| `/search <query>` | Grep code and symbols across the workspace. |
| `/files` | List files and directories in the workspace. |
| `/diff` | Display a syntax-highlighted git diff of local changes. |
| `/git` | View git status and active branch. |
| `/commit <msg>` | Stage changes and create a git commit. |
| `/terminal <cmd>` | Execute a one-off shell command. |
| `/undo` | Rollback the most recent file change via the backup snapshot. |
