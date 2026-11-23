# FireBox Security & Safety Guide

FireBox is designed with a defense-in-depth security model to ensure autonomous agent actions never harm your system or leak confidential credentials.

---

## Safety Levels

FireBox offers three configurable safety tiers:

| Tier | Name | Description |
| :--- | :--- | :--- |
| **STRICT** | Maximum Isolation | Requires explicit user approval for any file write, edit, deletion, or shell command. |
| **BALANCED** *(Default)* | Guarded Autonomy | Restricts file access strictly to workspace boundaries, blocks dangerous system commands, and prompts for destructive deletions or git push. |
| **AUTONOMOUS** | Full Velocity | Allows the agent to create files, edit code, and run tests automatically while strictly observing workspace boundaries. |

You can switch the safety level in `~/.firebox/permissions.json` or via:
```bash
firebox permissions
```

---

## Workspace Boundary Isolation

By default, `workspace_only` is set to `true`.
- Any file read, write, edit, or delete targeting a path outside the project directory is blocked immediately with an error:
  `Access blocked: path is outside workspace`
- Prevents the agent from reading or overwriting system files, other user projects, or host configurations.

---

## Blacklisted Sensitive Files

FireBox automatically blocks access to sensitive system paths and credentials, including:
- `.ssh/` directories and private keys (`id_rsa`, `id_ed25519`)
- Shell history files (`.bash_history`, `.zsh_history`)
- Windows Security Accounts Manager hives
- FireBox credential vaults (`credentials.dat`)

---

## Automatic Backups & Instant Rollback

Every time FireBox writes to an existing file, edits a file, or deletes a file:
1. It automatically saves a timestamped snapshot in `~/.firebox/backups/`.
2. If an edit produces unwanted behavior, type `/undo` in the interactive REPL:
   ```bash
   /undo
   ```
   FireBox will immediately restore the previous snapshot of the file.

---

## Audit Trail

Every file read, file write, shell command, git operation, and tool execution is recorded in an append-only JSON audit log:
`~/.firebox/logs/audit.log`

Each entry includes:
- Exact timestamp and ISO 8601 UTC time
- Action name and parameters
- Exit code / duration
- User approval status
