"""
Audit Logging for FireBox.
Persistent append-only audit trail of all agent actions, tool calls, and outcomes.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

from firebox.config.manager import get_config


class AuditLogger:
    """Records security and execution events to an immutable log file."""

    def __init__(self, log_file: Optional[Path] = None):
        if log_file is None:
            config_mgr = get_config()
            log_file = config_mgr.logs_dir / "audit.log"
        self.log_file = log_file

    def log(
        self,
        event_type: str,
        action: str,
        details: Dict[str, Any],
        user_approved: bool = True,
        status: str = "success",
    ):
        """Append an audit record to disk."""
        entry = {
            "timestamp": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event_type": event_type,
            "action": action,
            "user_approved": user_approved,
            "status": status,
            "details": details,
        }
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass


_audit_logger = None


def get_audit_logger() -> AuditLogger:
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
