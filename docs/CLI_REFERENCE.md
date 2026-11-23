# FireBox CLI Command Reference

This reference covers all top-level CLI commands and flags.

## Core Commands

### `firebox`
Launches the interactive cinematic TUI in the current working directory.
```bash
firebox
```

### `firebox [PATH]`
Target a specific directory as the workspace.
```bash
firebox C:\Users\dev\my-app
firebox .
```

### `firebox --prompt "<query>"` / `-p`
Execute a one-off prompt autonomously without opening the interactive REPL.
```bash
firebox -p "Analyze the files in this directory and write a README.md"
```

### `firebox init [PATH]`
Creates a customized `FIREBOX.md` project instruction template in the target workspace.
```bash
firebox init
```

### `firebox doctor`
Runs comprehensive system, environment, provider, and permission diagnostics.
```bash
firebox doctor
```

### `firebox setup`
Launches the interactive setup wizard to select providers and configure API keys.
```bash
firebox setup
```

### `firebox version` / `-v`
Displays the active FireBox version, codename, and tagline.
```bash
firebox version
```

---

## Project Subcommands

| Command | Usage | Description |
| :--- | :--- | :--- |
| `firebox plan <goal>` | `firebox plan "Add JWT authentication"` | Generates a structured milestone plan without editing code. |
| `firebox build <task>` | `firebox build "Implement user login route"` | Implements code changes directly with validation. |
| `firebox fix [issue]` | `firebox fix` | Diagnoses recent test failures or bugs and applies fixes. |
| `firebox test` | `firebox test` | Auto-detects and runs the project's test suite. |
| `firebox review` | `firebox review` | Performs a deep security and quality code review. |
| `firebox analyze` | `firebox analyze` | Detects programming languages, frameworks, and tools. |
| `firebox refactor <target>`| `firebox refactor "db.py"` | Refactors targeted modules for clarity and performance. |

---

## Provider & Model Commands

| Command | Description |
| :--- | :--- |
| `firebox providers` | List all supported and configured AI providers. |
| `firebox provider add <name> <key>` | Save API key for a provider. |
| `firebox provider test <name>` | Verify API credentials and connectivity. |
| `firebox models` | List available models for active provider. |
| `firebox models set <model_name>` | Set active default model. |

---

## Management Commands

| Command | Description |
| :--- | :--- |
| `firebox sessions` | List saved conversation sessions. |
| `firebox tools` | List all registered tools and their enabled status. |
| `firebox plugins` | List installed third-party plugins. |
| `firebox permissions` | View security level and workspace boundary rules. |
| `firebox reset` | Reset all configuration and cache to defaults. |
