"""
Shell & Process Execution Tools for FireBox.
Executes terminal commands, test runners, and build systems with security gates.
"""

import subprocess
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

from firebox.tools.base import BaseTool, ToolResult
from firebox.safety.permissions import PermissionManager
from firebox.safety.audit import get_audit_logger


class ShellExecTool(BaseTool):
    name = "shell_exec"
    description = "Execute a command in PowerShell (Windows) or bash (Linux/macOS) in the workspace."
    category = "execution"
    requires_permission = True

    def __init__(self, permissions: PermissionManager):
        self.permissions = permissions

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command line to execute.",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Execution timeout in seconds (default 60).",
                },
            },
            "required": ["command"],
        }

    def run(self, command: str, timeout: int = 60, **kwargs) -> ToolResult:
        start_t = time.time()

        risk_level, req_approval = self.permissions.assess_command_risk(command)
        if risk_level == "BLOCKED":
            return ToolResult(
                output="",
                success=False,
                error=f"Command '{command}' is permanently blocked by security policy.",
                duration_ms=(time.time() - start_t) * 1000,
            )

        if req_approval:
            approved = self.permissions.request_approval(
                f"Execute Shell Command [{risk_level}]",
                f"Command: {command}\nWorking Dir: {self.permissions.workspace_root}"
            )
            if not approved:
                return ToolResult(
                    output="",
                    success=False,
                    error="Command execution rejected by user.",
                    duration_ms=(time.time() - start_t) * 1000,
                )

        # Select shell: PowerShell on Windows, /bin/sh or bash on Unix
        shell_args = []
        if os.name == "nt":
            shell_args = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command]
        else:
            shell_args = ["/bin/bash", "-c", command]

        try:
            proc = subprocess.run(
                shell_args,
                cwd=str(self.permissions.workspace_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )
            out = proc.stdout
            err = proc.stderr
            code = proc.returncode

            combined = ""
            if out:
                combined += out
            if err:
                combined += ("\nSTDERR:\n" + err if combined else err)

            success = (code == 0)
            get_audit_logger().log("shell_exec", command, {"exit_code": code, "output_len": len(combined)})

            return ToolResult(
                output=combined or "(no output)",
                success=success,
                error=None if success else f"Process exited with code {code}",
                artifacts={"exit_code": code},
                duration_ms=(time.time() - start_t) * 1000,
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                output="",
                success=False,
                error=f"Command timed out after {timeout} seconds.",
                duration_ms=(time.time() - start_t) * 1000,
            )
        except Exception as e:
            return ToolResult(output="", success=False, error=str(e), duration_ms=(time.time() - start_t) * 1000)


class RunTestsTool(BaseTool):
    name = "run_tests"
    description = "Automatically detect the workspace testing framework (pytest, npm test, cargo test, etc.) and run test suite."
    category = "execution"

    def __init__(self, permissions: PermissionManager):
        self.permissions = permissions
        self.shell = ShellExecTool(permissions)

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "custom_command": {
                    "type": "string",
                    "description": "Optional custom test command override.",
                },
            },
        }

    def run(self, custom_command: Optional[str] = None, **kwargs) -> ToolResult:
        ws = self.permissions.workspace_root
        cmd = custom_command

        if not cmd:
            if (ws / "pytest.ini").exists() or (ws / "tests").exists() or (ws / "pyproject.toml").exists():
                cmd = "python -m pytest"
            elif (ws / "package.json").exists():
                cmd = "npm test"
            elif (ws / "Cargo.toml").exists():
                cmd = "cargo test"
            elif (ws / "go.mod").exists():
                cmd = "go test ./..."
            else:
                cmd = "python -m unittest discover"

        return self.shell.run(command=cmd, **kwargs)


class RunBuildTool(BaseTool):
    name = "run_build"
    description = "Detect and execute project build commands (npm run build, cargo build, etc.)."
    category = "execution"

    def __init__(self, permissions: PermissionManager):
        self.permissions = permissions
        self.shell = ShellExecTool(permissions)

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "custom_command": {
                    "type": "string",
                    "description": "Optional custom build command override.",
                },
            },
        }

    def run(self, custom_command: Optional[str] = None, **kwargs) -> ToolResult:
        ws = self.permissions.workspace_root
        cmd = custom_command

        if not cmd:
            if (ws / "package.json").exists():
                cmd = "npm run build"
            elif (ws / "Cargo.toml").exists():
                cmd = "cargo build"
            elif (ws / "pyproject.toml").exists():
                cmd = "python -m build"
            else:
                return ToolResult(output="", success=False, error="Could not determine build command automatically. Please specify custom_command.")

        return self.shell.run(command=cmd, **kwargs)
