"""
Central Tool Registry for FireBox.
Registers, indexes, verifies permissions, and executes all agent tools.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path

from firebox.tools.base import BaseTool, ToolResult
from firebox.tools.file_tools import ReadFileTool, WriteFileTool, EditFileTool, ListDirTool, DeleteFileTool
from firebox.tools.search_tools import FileSearchTool, TextSearchTool, CodeSymbolSearchTool
from firebox.tools.execution_tools import ShellExecTool, RunTestsTool, RunBuildTool
from firebox.tools.git_tools import GitStatusTool, GitDiffTool, GitCommitTool, GitLogTool
from firebox.tools.project_tools import DetectProjectTool, InspectDependenciesTool
from firebox.tools.web_tools import WebSearchTool, FetchUrlTool
from firebox.safety.permissions import PermissionManager


class ToolRegistry:
    """Manages the lifecycle and execution of all registered tools."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.permissions = PermissionManager(workspace_root)
        self._tools: Dict[str, BaseTool] = {}
        self._enabled: Dict[str, bool] = {}
        self._register_default_tools()

    def set_workspace(self, path: Path):
        self.permissions.set_workspace(path)

    def register(self, tool: BaseTool, enabled: bool = True):
        """Register a new tool instance."""
        self._tools[tool.name] = tool
        self._enabled[tool.name] = enabled

    def _register_default_tools(self):
        """Instantiate all built-in core tools."""
        default_tools = [
            ReadFileTool(self.permissions),
            WriteFileTool(self.permissions),
            EditFileTool(self.permissions),
            ListDirTool(self.permissions),
            DeleteFileTool(self.permissions),
            FileSearchTool(self.permissions),
            TextSearchTool(self.permissions),
            CodeSymbolSearchTool(self.permissions),
            ShellExecTool(self.permissions),
            RunTestsTool(self.permissions),
            RunBuildTool(self.permissions),
            GitStatusTool(self.permissions),
            GitDiffTool(self.permissions),
            GitCommitTool(self.permissions),
            GitLogTool(self.permissions),
            DetectProjectTool(self.permissions),
            InspectDependenciesTool(self.permissions),
            WebSearchTool(),
            FetchUrlTool(),
        ]
        for t in default_tools:
            self.register(t, enabled=True)

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def is_enabled(self, name: str) -> bool:
        return self._enabled.get(name, False)

    def enable_tool(self, name: str):
        if name in self._tools:
            self._enabled[name] = True

    def disable_tool(self, name: str):
        if name in self._tools:
            self._enabled[name] = False

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return list of metadata for all tools."""
        res = []
        for name, t in self._tools.items():
            res.append({
                "name": t.name,
                "description": t.description,
                "category": t.category,
                "is_destructive": t.is_destructive,
                "requires_permission": t.requires_permission,
                "enabled": self._enabled.get(name, True),
            })
        return res

    def get_openai_schemas(self) -> List[Dict[str, Any]]:
        """Return active tools in OpenAI function schemas format."""
        schemas = []
        for name, tool in self._tools.items():
            if self.is_enabled(name):
                schemas.append(tool.to_openai_schema())
        return schemas

    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Execute a tool by name with safety checks."""
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(output="", success=False, error=f"Unknown tool: '{name}'")
        if not self.is_enabled(name):
            return ToolResult(output="", success=False, error=f"Tool '{name}' is currently disabled.")

        try:
            return tool.run(**arguments)
        except Exception as e:
            return ToolResult(output="", success=False, error=f"Tool exception: {str(e)}")


_tool_registry = None


def get_tool_registry(workspace_root: Optional[Path] = None) -> ToolRegistry:
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry(workspace_root)
    elif workspace_root:
        _tool_registry.set_workspace(workspace_root)
    return _tool_registry
