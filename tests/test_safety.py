"""
Tests for Security, Workspace Isolation, Audit, and Rollback.
"""

import pytest
from pathlib import Path
from firebox.safety.permissions import PermissionManager
from firebox.safety.rollback import RollbackManager
from firebox.safety.audit import AuditLogger


def test_workspace_isolation(tmp_path):
    ws = tmp_path / "workspace"
    outside = tmp_path / "outside"
    ws.mkdir()
    outside.mkdir()

    outside_file = outside / "secret.txt"
    outside_file.write_text("classified", encoding="utf-8")

    perm = PermissionManager(ws)
    assert perm.is_within_workspace(ws / "file.txt") is True
    assert perm.is_within_workspace(outside_file) is False

    ok, err = perm.check_file_access(outside_file)
    assert ok is False
    assert "outside workspace" in err


def test_sensitive_pattern_blocking(tmp_path):
    perm = PermissionManager(tmp_path)
    ssh_key = tmp_path / ".ssh" / "id_rsa"
    ok, err = perm.check_file_access(ssh_key)
    assert ok is False
    assert "sensitive security pattern" in err


def test_command_risk_assessment(tmp_path):
    perm = PermissionManager(tmp_path)
    
    # Blocked
    risk, req = perm.assess_command_risk("rm -rf /")
    assert risk == "BLOCKED"
    assert req is True

    # Safe whitelisted
    risk, req = perm.assess_command_risk("git status")
    assert risk == "SAFE"
    assert req is False


def test_rollback_manager(tmp_path):
    backup_dir = tmp_path / "backups"
    rb = RollbackManager(backup_dir)

    target_file = tmp_path / "app.py"
    target_file.write_text("version 1.0", encoding="utf-8")

    # Backup
    bak = rb.backup_file(target_file)
    assert bak is not None
    assert bak.exists()

    # Modify
    target_file.write_text("corrupted content", encoding="utf-8")

    # Rollback
    success = rb.rollback_file(target_file)
    assert success is True
    assert target_file.read_text(encoding="utf-8") == "version 1.0"
