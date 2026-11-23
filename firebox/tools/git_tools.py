"""
Git Navigation & Operations Tools for FireBox.
Status, diff, commits, branch management, and repository analysis.
"""

import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional

from firebox.tools.base import BaseTool, ToolResult
from firebox.safety.permissions import PermissionManager
from firebox.safety.audit import get_audit_logger


class GitStatusTool(BaseTool):
    name = "git_status"
    description = "Check git status of the project repository (modified files, staged files, branch)."
    category = "git"

    def __init__(self, permissions: PermissionManager):
        self.permissions = permissions

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    def run(self, **kwargs) -> ToolResult:
        start_t = time.time()
        try:
            res = subprocess.run(
                ["git", "status", "--short", "--branch"],
                cwd=str(self.permissions.workspace_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if res.returncode != 0:
                return ToolResult(output="", success=False, error=res.stderr or "Not a git repository.")
            return ToolResult(output=res.stdout or "Clean working tree.", success=True, duration_ms=(time.time() - start_t) * 1000)
        except Exception as e:
            return ToolResult(output="", success=False, error=str(e), duration_ms=(time.time() - start_t) * 1000)


class GitDiffTool(BaseTool):
    name = "git_diff"
    description = "Show git diff of unstaged or staged changes in the workspace."
    category = "git"

    def __init__(self, permissions: PermissionManager):
        self.permissions = permissions

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "staged": {
                    "type": "boolean",
                    "description": "Show staged diff instead of unstaged diff. Default false.",
                },
                "filepath": {
                    "type": "string",
                    "description": "Specific file path to diff. Optional.",
                },
            },
        }

    def run(self, staged: bool = False, filepath: Optional[str] = None, **kwargs) -> ToolResult:
        start_t = time.time()
        args = ["git", "diff"]
        if staged:
            args.append("--staged")
        if filepath:
            args.append(filepath)

        try:
            res = subprocess.run(
                args,
                cwd=str(self.permissions.workspace_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if res.returncode != 0:
                return ToolResult(output="", success=False, error=res.stderr)
            diff_text = res.stdout
            return ToolResult(output=diff_text or "No git diff changes.", success=True, duration_ms=(time.time() - start_t) * 1000)
        except Exception as e:
            return ToolResult(output="", success=False, error=str(e), duration_ms=(time.time() - start_t) * 1000)


class GitCommitTool(BaseTool):
    name = "git_commit"
    description = "Stage files and create a git commit with a descriptive message."
    category = "git"
    requires_permission = True

    def __init__(self, permissions: PermissionManager):
        self.permissions = permissions

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Commit message.",
                },
                "stage_all": {
                    "type": "boolean",
                    "description": "Whether to stage all tracked/untracked modified files. Default true.",
                },
            },
            "required": ["message"],
        }

    def run(self, message: str, stage_all: bool = True, **kwargs) -> ToolResult:
        start_t = time.time()
        try:
            if stage_all:
                subprocess.run(["git", "add", "-A"], cwd=str(self.permissions.workspace_root), check=True)
            res = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=str(self.permissions.workspace_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if res.returncode != 0:
                return ToolResult(output="", success=False, error=res.stderr or res.stdout)
            get_audit_logger().log("git_commit", message, {})
            return ToolResult(output=res.stdout, success=True, duration_ms=(time.time() - start_t) * 1000)
        except Exception as e:
            return ToolResult(output="", success=False, error=str(e), duration_ms=(time.time() - start_t) * 1000)


class GitLogTool(BaseTool):
    name = "git_log"
    description = "View recent git commit history."
    category = "git"

    def __init__(self, permissions: PermissionManager):
        self.permissions = permissions

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of commits to return (default 10).",
                },
            },
        }

    def run(self, limit: int = 10, **kwargs) -> ToolResult:
        start_t = time.time()
        try:
            res = subprocess.run(
                ["git", "log", f"-n{limit}", "--oneline", "--decorate"],
                cwd=str(self.permissions.workspace_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            return ToolResult(output=res.stdout or "No commits yet.", success=True, duration_ms=(time.time() - start_t) * 1000)
        except Exception as e:
            return ToolResult(output="", success=False, error=str(e), duration_ms=(time.time() - start_t) * 1000)
