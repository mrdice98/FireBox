"""
Search & Code Navigation Tools for FireBox.
File path searches, regex grep across codebase, and code symbol extraction.
"""

import os
import re
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from firebox.tools.base import BaseTool, ToolResult
from firebox.safety.permissions import PermissionManager


class FileSearchTool(BaseTool):
    name = "file_search"
    description = "Search for files by glob or substring pattern in the workspace."
    category = "search"

    def __init__(self, permissions: PermissionManager):
        self.permissions = permissions

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Filename pattern to match (e.g. '*.py', 'test*', 'package.json').",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 50).",
                },
            },
            "required": ["pattern"],
        }

    def run(self, pattern: str, max_results: int = 50, **kwargs) -> ToolResult:
        start_t = time.time()
        ignored = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
        matches = []

        try:
            for root, dirs, files in os.walk(self.permissions.workspace_root):
                dirs[:] = [d for d in dirs if d not in ignored]
                for f in files:
                    # Glob pattern match or substring match
                    if Path(f).match(pattern) or pattern.lower() in f.lower():
                        full_p = Path(root) / f
                        rel_p = full_p.relative_to(self.permissions.workspace_root)
                        matches.append(str(rel_p))
                        if len(matches) >= max_results:
                            break
                if len(matches) >= max_results:
                    break

            output = "\n".join(matches) if matches else "No matching files found."
            return ToolResult(
                output=output,
                success=True,
                artifacts={"count": len(matches)},
                duration_ms=(time.time() - start_t) * 1000,
            )
        except Exception as e:
            return ToolResult(output="", success=False, error=str(e), duration_ms=(time.time() - start_t) * 1000)


class TextSearchTool(BaseTool):
    name = "text_search"
    description = "Search for a text pattern or regex across all project files (like ripgrep / grep)."
    category = "search"

    def __init__(self, permissions: PermissionManager):
        self.permissions = permissions

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Text substring or regex pattern to search for in files.",
                },
                "case_sensitive": {
                    "type": "boolean",
                    "description": "Whether to perform case-sensitive search. Default false.",
                },
                "extension": {
                    "type": "string",
                    "description": "Optional file extension filter (e.g. '.py', '.ts').",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Max matching lines to return (default 100).",
                },
            },
            "required": ["query"],
        }

    def run(
        self,
        query: str,
        case_sensitive: bool = False,
        extension: Optional[str] = None,
        max_results: int = 100,
        **kwargs,
    ) -> ToolResult:
        start_t = time.time()
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            pattern = re.compile(query, flags)
        except re.error:
            # Fallback to literal
            pattern = re.compile(re.escape(query), flags)

        ignored = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
        results = []

        try:
            for root, dirs, files in os.walk(self.permissions.workspace_root):
                dirs[:] = [d for d in dirs if d not in ignored]
                for file_name in files:
                    if extension and not file_name.endswith(extension):
                        continue
                    full_p = Path(root) / file_name
                    # Skip large binary files
                    if full_p.stat().st_size > 2 * 1024 * 1024:
                        continue

                    try:
                        with open(full_p, "r", encoding="utf-8", errors="ignore") as f:
                            for idx, line in enumerate(f, 1):
                                if pattern.search(line):
                                    rel_p = full_p.relative_to(self.permissions.workspace_root)
                                    results.append(f"{rel_p}:{idx}: {line.strip()}")
                                    if len(results) >= max_results:
                                        break
                    except Exception:
                        continue
                    if len(results) >= max_results:
                        break
                if len(results) >= max_results:
                    break

            output = "\n".join(results) if results else "No matches found."
            return ToolResult(
                output=output,
                success=True,
                artifacts={"count": len(results)},
                duration_ms=(time.time() - start_t) * 1000,
            )
        except Exception as e:
            return ToolResult(output="", success=False, error=str(e), duration_ms=(time.time() - start_t) * 1000)


class CodeSymbolSearchTool(BaseTool):
    name = "code_symbol_search"
    description = "Search for function, class, interface, or method definitions in the codebase."
    category = "search"

    def __init__(self, permissions: PermissionManager):
        self.permissions = permissions

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Symbol name or substring (e.g. 'AuthService', 'calculate_tax').",
                },
            },
            "required": ["symbol"],
        }

    def run(self, symbol: str, **kwargs) -> ToolResult:
        start_t = time.time()
        # Common definition regexes across Python, JS/TS, Go, Rust, Java, C#
        regexes = [
            rf"(?:def|class|async\s+def)\s+({re.escape(symbol)}[a-zA-Z0-9_]*)",
            rf"(?:function|class|interface|type)\s+({re.escape(symbol)}[a-zA-Z0-9_]*)",
            rf"(?:const|let|var)\s+({re.escape(symbol)}[a-zA-Z0-9_]*)\s*=",
            rf"(?:fn|struct|enum|trait|impl)\s+({re.escape(symbol)}[a-zA-Z0-9_]*)",
            rf"(?:func)\s+(?:\([^\)]+\)\s+)?({re.escape(symbol)}[a-zA-Z0-9_]*)",
        ]
        combined = re.compile("|".join(regexes), re.IGNORECASE)

        matches = []
        ignored = {".git", "node_modules", "__pycache__", ".venv", "venv"}

        try:
            for root, dirs, files in os.walk(self.permissions.workspace_root):
                dirs[:] = [d for d in dirs if d not in ignored]
                for file_name in files:
                    if not file_name.endswith((".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".cs", ".cpp")):
                        continue
                    full_p = Path(root) / file_name
                    try:
                        with open(full_p, "r", encoding="utf-8", errors="ignore") as f:
                            for idx, line in enumerate(f, 1):
                                if combined.search(line):
                                    rel_p = full_p.relative_to(self.permissions.workspace_root)
                                    matches.append(f"{rel_p}:{idx}: {line.strip()}")
                    except Exception:
                        continue

            output = "\n".join(matches) if matches else f"No definitions found for symbol '{symbol}'."
            return ToolResult(output=output, success=True, duration_ms=(time.time() - start_t) * 1000)
        except Exception as e:
            return ToolResult(output="", success=False, error=str(e), duration_ms=(time.time() - start_t) * 1000)
