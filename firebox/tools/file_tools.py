"""
File System Tools for FireBox.
Safe, audited file reading, writing, editing, and directory navigation.
"""

import os
import shutil
import time
from pathlib import Path
from typing import Dict, Any, Optional

from firebox.tools.base import BaseTool, ToolResult
from firebox.safety.permissions import PermissionManager
from firebox.safety.rollback import get_rollback_manager
from firebox.safety.audit import get_audit_logger


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read the contents of a file in the workspace with optional line offset and limit."
    category = "file"

    def __init__(self, permissions: PermissionManager):
        self.permissions = permissions

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file relative to the project workspace.",
                },
                "offset": {
                    "type": "integer",
                    "description": "Starting line number (1-indexed). Optional.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of lines to return. Optional.",
                },
            },
            "required": ["path"],
        }

    def run(self, path: str, offset: Optional[int] = 1, limit: Optional[int] = 500, **kwargs) -> ToolResult:
        start_t = time.time()
        file_path = (self.permissions.workspace_root / path).resolve()

        ok, err = self.permissions.check_file_access(file_path, is_write=False)
        if not ok:
            return ToolResult(output="", success=False, error=err, duration_ms=(time.time() - start_t) * 1000)

        if not file_path.exists():
            return ToolResult(output="", success=False, error=f"File not found: {path}", duration_ms=(time.time() - start_t) * 1000)

        if not file_path.is_file():
            return ToolResult(output="", success=False, error=f"Path is not a file: {path}", duration_ms=(time.time() - start_t) * 1000)

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            total_lines = len(lines)
            start_idx = max(0, (offset or 1) - 1)
            end_idx = min(total_lines, start_idx + (limit or 500))

            selected_lines = lines[start_idx:end_idx]
            output_lines = [f"{i + 1:4d} | {line}" for i, line in enumerate(selected_lines, start=start_idx)]
            content = "".join(output_lines)

            get_audit_logger().log("file_read", path, {"total_lines": total_lines, "read_lines": len(selected_lines)})
            return ToolResult(
                output=content,
                success=True,
                artifacts={"total_lines": total_lines, "read_lines": len(selected_lines)},
                duration_ms=(time.time() - start_t) * 1000,
            )
        except Exception as e:
            return ToolResult(output="", success=False, error=str(e), duration_ms=(time.time() - start_t) * 1000)


class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Create or overwrite a file in the workspace. Automatically creates parent directories and backup."
    category = "file"
    is_destructive = False

    def __init__(self, permissions: PermissionManager):
        self.permissions = permissions
        self.rollback = get_rollback_manager()

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file relative to the project workspace.",
                },
                "content": {
                    "type": "string",
                    "description": "Full text content to write to the file.",
                },
            },
            "required": ["path", "content"],
        }

    def run(self, path: str, content: str, **kwargs) -> ToolResult:
        start_t = time.time()
        file_path = (self.permissions.workspace_root / path).resolve()

        ok, err = self.permissions.check_file_access(file_path, is_write=True)
        if not ok:
            return ToolResult(output="", success=False, error=err, duration_ms=(time.time() - start_t) * 1000)

        # Snapshot for rollback if overwriting existing file
        if file_path.exists():
            self.rollback.backup_file(file_path)

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            get_audit_logger().log("file_write", path, {"bytes": len(content.encode('utf-8'))})
            return ToolResult(
                output=f"Successfully wrote {len(content.splitlines())} lines to {path}",
                success=True,
                duration_ms=(time.time() - start_t) * 1000,
            )
        except Exception as e:
            return ToolResult(output="", success=False, error=str(e), duration_ms=(time.time() - start_t) * 1000)


class EditFileTool(BaseTool):
    name = "edit_file"
    description = "Make precise targeted text replacements in an existing file. Target must match existing text exactly."
    category = "file"

    def __init__(self, permissions: PermissionManager):
        self.permissions = permissions
        self.rollback = get_rollback_manager()

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file relative to project workspace.",
                },
                "target": {
                    "type": "string",
                    "description": "Exact text snippet to find and replace.",
                },
                "replacement": {
                    "type": "string",
                    "description": "New text to substitute in place of target.",
                },
            },
            "required": ["path", "target", "replacement"],
        }

    def run(self, path: str, target: str, replacement: str, **kwargs) -> ToolResult:
        start_t = time.time()
        file_path = (self.permissions.workspace_root / path).resolve()

        ok, err = self.permissions.check_file_access(file_path, is_write=True)
        if not ok:
            return ToolResult(output="", success=False, error=err, duration_ms=(time.time() - start_t) * 1000)

        if not file_path.exists() or not file_path.is_file():
            return ToolResult(output="", success=False, error=f"File not found: {path}", duration_ms=(time.time() - start_t) * 1000)

        try:
            content = file_path.read_text(encoding="utf-8")
            if target not in content:
                return ToolResult(
                    output="",
                    success=False,
                    error=f"Target snippet not found in {path}. Make sure whitespace and formatting match exactly.",
                    duration_ms=(time.time() - start_t) * 1000,
                )

            # Backup before edit
            self.rollback.backup_file(file_path)

            count = content.count(target)
            new_content = content.replace(target, replacement)
            file_path.write_text(new_content, encoding="utf-8")

            get_audit_logger().log("file_edit", path, {"occurrences_replaced": count})
            return ToolResult(
                output=f"Successfully replaced {count} occurrence(s) in {path}.",
                success=True,
                duration_ms=(time.time() - start_t) * 1000,
            )
        except Exception as e:
            return ToolResult(output="", success=False, error=str(e), duration_ms=(time.time() - start_t) * 1000)


class ListDirTool(BaseTool):
    name = "list_dir"
    description = "List files and directories in a given workspace path with file sizes and type indications."
    category = "file"

    def __init__(self, permissions: PermissionManager):
        self.permissions = permissions

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path relative to workspace root (defaults to workspace root).",
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Whether to list recursively (depth 2 max). Default false.",
                },
            },
        }

    def run(self, path: str = ".", recursive: bool = False, **kwargs) -> ToolResult:
        start_t = time.time()
        dir_path = (self.permissions.workspace_root / path).resolve()

        ok, err = self.permissions.check_file_access(dir_path, is_write=False)
        if not ok:
            return ToolResult(output="", success=False, error=err, duration_ms=(time.time() - start_t) * 1000)

        if not dir_path.exists() or not dir_path.is_dir():
            return ToolResult(output="", success=False, error=f"Directory not found: {path}", duration_ms=(time.time() - start_t) * 1000)

        try:
            entries = []
            ignored = {".git", "node_modules", "__pycache__", ".venv", "venv", ".pytest_cache"}

            if not recursive:
                for item in sorted(dir_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
                    if item.name in ignored:
                        continue
                    if item.is_dir():
                        entries.append(f"[DIR]  {item.name}/")
                    else:
                        size_kb = item.stat().st_size / 1024
                        entries.append(f"[FILE] {item.name:<30} ({size_kb:.1f} KB)")
            else:
                for root, dirs, files in os.walk(dir_path):
                    dirs[:] = [d for d in dirs if d not in ignored]
                    rel_root = Path(root).relative_to(self.permissions.workspace_root)
                    if len(rel_root.parts) > 3:
                        continue
                    for d in dirs:
                        entries.append(f"[DIR]  {rel_root / d}/")
                    for f in files:
                        entries.append(f"[FILE] {rel_root / f}")

            output = "\n".join(entries) if entries else "(empty directory)"
            return ToolResult(
                output=output,
                success=True,
                artifacts={"count": len(entries)},
                duration_ms=(time.time() - start_t) * 1000,
            )
        except Exception as e:
            return ToolResult(output="", success=False, error=str(e), duration_ms=(time.time() - start_t) * 1000)


class DeleteFileTool(BaseTool):
    name = "delete_file"
    description = "Delete a file or directory in the workspace. Sensitive operation requiring approval."
    category = "file"
    is_destructive = True
    requires_permission = True

    def __init__(self, permissions: PermissionManager):
        self.permissions = permissions
        self.rollback = get_rollback_manager()

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to file or folder to delete relative to workspace.",
                },
            },
            "required": ["path"],
        }

    def run(self, path: str, **kwargs) -> ToolResult:
        start_t = time.time()
        target_path = (self.permissions.workspace_root / path).resolve()

        ok, err = self.permissions.check_file_access(target_path, is_write=True)
        if not ok:
            return ToolResult(output="", success=False, error=err, duration_ms=(time.time() - start_t) * 1000)

        if not target_path.exists():
            return ToolResult(output="", success=False, error=f"Target does not exist: {path}", duration_ms=(time.time() - start_t) * 1000)

        # Safety approval check
        approved = self.permissions.request_approval(
            "Delete File / Directory",
            f"Permanent deletion of: {path} ({target_path})"
        )
        if not approved:
            return ToolResult(output="", success=False, error="Operation rejected by user.", duration_ms=(time.time() - start_t) * 1000)

        try:
            if target_path.is_file():
                self.rollback.backup_file(target_path)
                target_path.unlink()
            elif target_path.is_dir():
                shutil.rmtree(target_path)

            get_audit_logger().log("delete", path, {"resolved": str(target_path)})
            return ToolResult(output=f"Successfully deleted {path}", success=True, duration_ms=(time.time() - start_t) * 1000)
        except Exception as e:
            return ToolResult(output="", success=False, error=str(e), duration_ms=(time.time() - start_t) * 1000)
