"""
Safety and Permission Enforcement for FireBox.
Workspace boundary isolation, risk level assessment, and user approval gates.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from firebox.config.manager import get_config
from firebox.config.schemas import SafetyLevel
from firebox.ui.formatters import render_approval_prompt


class PermissionManager:
    """Evaluates and enforces tool execution permissions and workspace boundaries."""

    def __init__(self, workspace_root: Optional[Path] = None):
        if workspace_root is None:
            workspace_root = Path.cwd().resolve()
        self.workspace_root = workspace_root.resolve()
        self.config_mgr = get_config()
        self.always_approved_actions = set()

    def set_workspace(self, path: Path):
        self.workspace_root = path.resolve()

    def is_within_workspace(self, target_path: Path) -> bool:
        """Verify whether a target file path resides strictly inside the active workspace."""
        try:
            resolved = target_path.resolve()
            # Allow workspace itself and anything underneath
            return resolved == self.workspace_root or self.workspace_root in resolved.parents
        except Exception:
            return False

    def check_file_access(self, target_path: Path, is_write: bool = False) -> Tuple[bool, Optional[str]]:
        """Verify file operation safety against workspace boundaries and sensitive files."""
        resolved = target_path.resolve()

        # Sensitive system / credentials blacklist (exact directory or exact file patterns)
        sensitive_patterns = [
            ".ssh", "id_rsa", "id_ed25519", ".bash_history", ".zsh_history",
            "credentials.dat", ".env.production", r"\system32\config\sam", r"/system32/config/sam"
        ]
        target_str = str(resolved).lower()
        for pat in sensitive_patterns:
            if pat.lower() in target_str:
                return False, f"Access blocked: target matches sensitive security pattern '{pat}'"

        # Check workspace restriction
        if self.config_mgr.permissions.workspace_only:
            if not self.is_within_workspace(resolved):
                return False, f"Access blocked: path '{resolved}' is outside workspace '{self.workspace_root}'"

        return True, None

    def assess_command_risk(self, command: str) -> Tuple[str, bool]:
        """Assess the risk of a shell command: (risk_level, requires_approval)."""
        cmd_lower = command.strip().lower()

        # Check blocked commands
        for blocked in self.config_mgr.permissions.blocked_commands:
            if blocked in cmd_lower:
                return "BLOCKED", True

        # Check whitelisted commands
        for white in self.config_mgr.permissions.whitelisted_commands:
            if cmd_lower.startswith(white.lower()):
                return "SAFE", False

        # Known dangerous operations
        high_risk_keywords = [
            "git push", "git reset --hard", "git clean -f",
            "rm -rf", "del /f", "drop database", "sudo",
            "chmod 777", "pip install -e", "npm install -g"
        ]
        for kw in high_risk_keywords:
            if kw in cmd_lower:
                return "HIGH_RISK", True

        safety = self.config_mgr.permissions.safety_level
        if safety == SafetyLevel.STRICT:
            return "MEDIUM_RISK", True
        elif safety == SafetyLevel.BALANCED:
            # Only prompt if destructive keywords found or outside whitelist
            return "NORMAL", True
        else: # AUTONOMOUS
            return "LOW_RISK", False

    def request_approval(self, action_name: str, details: str) -> bool:
        """Prompt user for approval if not already permanently approved."""
        key = f"{action_name}:{details}"
        if key in self.always_approved_actions:
            return True

        approved = render_approval_prompt(action_name, details)
        if approved:
            return True
        return False
