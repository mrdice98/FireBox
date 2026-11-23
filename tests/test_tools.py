"""
Tests for Modular Tools: File, Search, Execution, Git, Project.
"""

import pytest
from pathlib import Path
from firebox.tools.registry import ToolRegistry
from firebox.safety.permissions import PermissionManager
from firebox.tools.file_tools import ReadFileTool, WriteFileTool, EditFileTool, ListDirTool, DeleteFileTool
from firebox.tools.search_tools import FileSearchTool, TextSearchTool, CodeSymbolSearchTool
from firebox.tools.project_tools import DetectProjectTool, InspectDependenciesTool


def test_file_tools(tmp_path):
    perm = PermissionManager(tmp_path)
    write_tool = WriteFileTool(perm)
    read_tool = ReadFileTool(perm)
    edit_tool = EditFileTool(perm)
    list_tool = ListDirTool(perm)

    # 1. Write file
    w_res = write_tool.run(path="sample.txt", content="Hello FireBox!\nLine 2\nLine 3")
    assert w_res.success is True
    assert (tmp_path / "sample.txt").exists()

    # 2. Read file
    r_res = read_tool.run(path="sample.txt", offset=1, limit=2)
    assert r_res.success is True
    assert "Hello FireBox!" in r_res.output

    # 3. Edit file
    e_res = edit_tool.run(path="sample.txt", target="Line 2", replacement="Modified Line 2")
    assert e_res.success is True
    assert "Modified Line 2" in (tmp_path / "sample.txt").read_text(encoding="utf-8")

    # 4. List directory
    l_res = list_tool.run(path=".")
    assert l_res.success is True
    assert "sample.txt" in l_res.output


def test_search_tools(tmp_path):
    perm = PermissionManager(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "service.py").write_text("class AuthService:\n    def login(self):\n        return True\n", encoding="utf-8")

    fsearch = FileSearchTool(perm)
    tsearch = TextSearchTool(perm)
    csearch = CodeSymbolSearchTool(perm)

    # File search
    res = fsearch.run(pattern="*.py")
    assert res.success is True
    assert "service.py" in res.output

    # Text search
    res2 = tsearch.run(query="login")
    assert res2.success is True
    assert "def login" in res2.output

    # Code symbol search
    res3 = csearch.run(symbol="AuthService")
    assert res3.success is True
    assert "class AuthService" in res3.output


def test_project_detection(tmp_path):
    perm = PermissionManager(tmp_path)
    (tmp_path / "requirements.txt").write_text("fastapi==0.100.0\npytest\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test-pkg'\n", encoding="utf-8")

    det_tool = DetectProjectTool(perm)
    res = det_tool.run()
    assert res.success is True
    assert "Python" in res.output
    assert "FastAPI" in res.output
    assert "pytest" in res.output
