"""
File Backup and Rollback Manager for FireBox.
Stores file snapshots before mutations to allow instant undo/rollback.
"""

import shutil
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

from firebox.config.manager import get_config


class RollbackManager:
    """Manages snapshots of modified files for safe rollbacks."""

    def __init__(self, backups_dir: Optional[Path] = None):
        if backups_dir is None:
            config_mgr = get_config()
            backups_dir = config_mgr.backups_dir
        self.backups_dir = backups_dir
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        self.history: List[Dict[str, Any]] = []

    def backup_file(self, target_path: Path) -> Optional[Path]:
        """Create a timestamped copy of the target file prior to modification."""
        resolved = target_path.resolve()
        if not resolved.exists() or not resolved.is_file():
            return None

        timestamp = int(time.time() * 1000)
        backup_name = f"{resolved.name}.{timestamp}.bak"
        backup_path = self.backups_dir / backup_name

        try:
            shutil.copy2(resolved, backup_path)
            self.history.append({
                "target": str(resolved),
                "backup": str(backup_path),
                "timestamp": timestamp,
            })
            return backup_path
        except Exception:
            return None

    def rollback_file(self, target_path: Path) -> bool:
        """Restore the most recent backup of the specified file."""
        resolved = str(target_path.resolve())
        for item in reversed(self.history):
            if item["target"] == resolved:
                backup_path = Path(item["backup"])
                if backup_path.exists():
                    try:
                        shutil.copy2(backup_path, Path(resolved))
                        return True
                    except Exception:
                        return False
        return False

    def undo_last(self) -> Optional[str]:
        """Undo the most recent file change across the workspace."""
        if not self.history:
            return None
        last = self.history.pop()
        target = Path(last["target"])
        backup = Path(last["backup"])
        if backup.exists():
            try:
                shutil.copy2(backup, target)
                return str(target)
            except Exception:
                return None
        return None


_rollback_manager = None


def get_rollback_manager() -> RollbackManager:
    global _rollback_manager
    if _rollback_manager is None:
        _rollback_manager = RollbackManager()
    return _rollback_manager
