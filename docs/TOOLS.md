# FireBox Tool Registry Reference

FireBox comes preloaded with 19 core tools for workspace inspection, code modification, testing, and research.

---

## Tool Categories

### 1. File Tools
- `read_file(path, offset, limit)`: Reads lines from a file with optional offsets.
- `write_file(path, content)`: Creates or replaces a file with automatic parent folder creation and rollback snapshot.
- `edit_file(path, target, replacement)`: Replaces exact text snippets with pre-edit backup.
- `list_dir(path, recursive)`: Lists files and subdirectories with sizes and file counts.
- `delete_file(path)`: Destructive operation requiring approval in BALANCED/STRICT modes. Automatically backed up before deletion.

### 2. Search Tools
- `file_search(pattern)`: Finds files by glob or substring matching across the project.
- `text_search(query, case_sensitive, extension)`: Fast regex/literal grep search across all files with line numbers.
- `code_symbol_search(symbol)`: Extracts class, function, struct, interface, and method definitions across 10+ languages.

### 3. Execution Tools
- `shell_exec(command, timeout)`: Runs a command in PowerShell (Windows) or Bash (Linux/macOS) with timeout and risk vetting.
- `run_tests(custom_command)`: Auto-detects pytest, npm test, cargo test, or go test.
- `run_build(custom_command)`: Runs npm build, cargo build, or python build.

### 4. Git Tools
- `git_status()`: Summarizes staged, unstaged, untracked files, and current branch.
- `git_diff(staged, filepath)`: Unified diff output.
- `git_commit(message, stage_all)`: Stages and commits changes with audit logging.
- `git_log(limit)`: Displays recent commit history.

### 5. Project Tools
- `detect_project()`: Scans the workspace to identify languages, frameworks, test runners, and package managers.
- `inspect_dependencies()`: Reads requirements.txt, package.json, and Cargo.toml.

### 6. Web Tools
- `web_search(query)`: Performs live web search via Tavily API or DuckDuckGo fallback.
- `fetch_url(url)`: Fetches and converts public web documentation into clean Markdown.
