"""
Project Intelligence & Dependency Inspection Tools for FireBox.
Detects programming languages, frameworks, configurations, and dependencies.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List

from firebox.tools.base import BaseTool, ToolResult
from firebox.safety.permissions import PermissionManager


class DetectProjectTool(BaseTool):
    name = "detect_project"
    description = "Analyze the workspace to detect programming languages, web/backend frameworks, and tooling."
    category = "project"

    def __init__(self, permissions: PermissionManager):
        self.permissions = permissions

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    def run(self, **kwargs) -> ToolResult:
        start_t = time.time()
        ws = self.permissions.workspace_root

        info = {
            "root": str(ws),
            "languages": [],
            "frameworks": [],
            "package_managers": [],
            "test_runners": [],
            "config_files": [],
        }

        # Check files
        signatures = {
            "pyproject.toml": ("Python", "pip/poetry/uv", "pyproject.toml"),
            "setup.py": ("Python", "setuptools", "setup.py"),
            "requirements.txt": ("Python", "pip", "requirements.txt"),
            "package.json": ("JavaScript/TypeScript", "npm/yarn/pnpm", "package.json"),
            "tsconfig.json": ("TypeScript", None, "tsconfig.json"),
            "Cargo.toml": ("Rust", "cargo", "Cargo.toml"),
            "go.mod": ("Go", "go mod", "go.mod"),
            "pom.xml": ("Java", "maven", "pom.xml"),
            "build.gradle": ("Java/Kotlin", "gradle", "build.gradle"),
            "CMakeLists.txt": ("C/C++", "cmake", "CMakeLists.txt"),
            "Makefile": ("C/C++/Generic", "make", "Makefile"),
            "Dockerfile": ("DevOps", "docker", "Dockerfile"),
            ".git": ("VCS", "git", ".git"),
        }

        for file_name, (lang, pm, cfg) in signatures.items():
            if (ws / file_name).exists():
                if lang and lang not in info["languages"]:
                    info["languages"].append(lang)
                if pm and pm not in info["package_managers"]:
                    info["package_managers"].append(pm)
                info["config_files"].append(cfg)

        # Inspect package.json for frameworks
        pkg_json = ws / "package.json"
        if pkg_json.exists():
            try:
                data = json.loads(pkg_json.read_text(encoding="utf-8"))
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                if "next" in deps:
                    info["frameworks"].append("Next.js")
                if "react" in deps:
                    info["frameworks"].append("React")
                if "vue" in deps:
                    info["frameworks"].append("Vue")
                if "svelte" in deps:
                    info["frameworks"].append("Svelte")
                if "express" in deps:
                    info["frameworks"].append("Express")
                if "tailwindcss" in deps:
                    info["frameworks"].append("Tailwind CSS")
                if "jest" in deps or "vitest" in deps:
                    info["test_runners"].append("Jest/Vitest")
            except Exception:
                pass

        # Inspect python requirements/pyproject
        reqs = ws / "requirements.txt"
        if reqs.exists():
            try:
                txt = reqs.read_text(encoding="utf-8").lower()
                if "fastapi" in txt:
                    info["frameworks"].append("FastAPI")
                if "django" in txt:
                    info["frameworks"].append("Django")
                if "flask" in txt:
                    info["frameworks"].append("Flask")
                if "pytest" in txt:
                    info["test_runners"].append("pytest")
            except Exception:
                pass

        summary_lines = [
            f"Project Root: {info['root']}",
            f"Languages: {', '.join(info['languages']) or 'Unknown'}",
            f"Frameworks: {', '.join(info['frameworks']) or 'None detected'}",
            f"Package Managers: {', '.join(info['package_managers']) or 'None'}",
            f"Test Runners: {', '.join(info['test_runners']) or 'None'}",
            f"Config Files: {', '.join(info['config_files']) or 'None'}",
        ]
        return ToolResult(
            output="\n".join(summary_lines),
            success=True,
            artifacts=info,
            duration_ms=(time.time() - start_t) * 1000,
        )


class InspectDependenciesTool(BaseTool):
    name = "inspect_dependencies"
    description = "Read and list installed or declared dependencies in package.json, requirements.txt, Cargo.toml, etc."
    category = "project"

    def __init__(self, permissions: PermissionManager):
        self.permissions = permissions

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    def run(self, **kwargs) -> ToolResult:
        start_t = time.time()
        ws = self.permissions.workspace_root
        results = []

        # Python requirements
        req_p = ws / "requirements.txt"
        if req_p.exists():
            results.append("=== requirements.txt ===\n" + req_p.read_text(encoding="utf-8", errors="replace"))

        # Node package.json
        pkg_p = ws / "package.json"
        if pkg_p.exists():
            try:
                data = json.loads(pkg_p.read_text(encoding="utf-8"))
                deps = data.get("dependencies", {})
                dev_deps = data.get("devDependencies", {})
                results.append("=== package.json Dependencies ===\n" + json.dumps(deps, indent=2))
                results.append("=== package.json DevDependencies ===\n" + json.dumps(dev_deps, indent=2))
            except Exception as e:
                results.append(f"package.json parse error: {e}")

        # Cargo.toml
        cargo_p = ws / "Cargo.toml"
        if cargo_p.exists():
            results.append("=== Cargo.toml ===\n" + cargo_p.read_text(encoding="utf-8", errors="replace"))

        output = "\n\n".join(results) if results else "No standard dependency files found."
        return ToolResult(output=output, success=True, duration_ms=(time.time() - start_t) * 1000)
