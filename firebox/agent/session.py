"""
Persistent Session Management for FireBox.
Saves, resumes, lists, and exports conversation sessions and checkpoints.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from firebox.providers.base import ChatMessage
from firebox.agent.planner import ExecutionPlan
from firebox.agent.modes import AgentMode
from firebox.config.manager import get_config


class SessionData(BaseModel):
    session_id: str
    workspace_root: str
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    mode: str = AgentMode.AUTONOMOUS.value
    provider: str = "openai"
    model: str = "gpt-4o"
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    plan: Optional[Dict[str, Any]] = None
    checkpoints: List[Dict[str, Any]] = Field(default_factory=list)


class SessionManager:
    """Manages persistent sessions stored in ~/.firebox/sessions/."""

    def __init__(self, sessions_dir: Optional[Path] = None):
        if sessions_dir is None:
            config_mgr = get_config()
            sessions_dir = config_mgr.sessions_dir
        self.sessions_dir = sessions_dir
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, session_id: str) -> Path:
        safe_id = "".join(c for c in session_id if c.isalnum() or c in ("-", "_"))
        return self.sessions_dir / f"{safe_id}.json"

    def save_session(
        self,
        session_id: str,
        workspace_root: Path,
        messages: List[ChatMessage],
        plan: Optional[ExecutionPlan] = None,
        mode: AgentMode = AgentMode.AUTONOMOUS,
        provider: str = "openai",
        model: str = "gpt-4o",
    ) -> Path:
        """Persist session state to JSON file."""
        path = self._get_path(session_id)
        msg_dicts = [m.model_dump() for m in messages]
        plan_dict = plan.model_dump() if plan else None

        session_obj = SessionData(
            session_id=session_id,
            workspace_root=str(workspace_root),
            updated_at=time.time(),
            mode=mode.value,
            provider=provider,
            model=model,
            messages=msg_dicts,
            plan=plan_dict,
        )
        path.write_text(json.dumps(session_obj.model_dump(), indent=2), encoding="utf-8")
        return path

    def load_session(self, session_id: str) -> Optional[SessionData]:
        """Load session state from disk."""
        path = self._get_path(session_id)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return SessionData(**data)
        except Exception:
            return None

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all saved sessions with metadata."""
        results = []
        for p in sorted(self.sessions_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                results.append({
                    "session_id": data.get("session_id", p.stem),
                    "workspace": data.get("workspace_root", ""),
                    "mode": data.get("mode", "autonomous"),
                    "model": data.get("model", ""),
                    "message_count": len(data.get("messages", [])),
                    "updated_at": data.get("updated_at", p.stat().st_mtime),
                })
            except Exception:
                continue
        return results

    def export_session_markdown(self, session_id: str, output_path: Optional[Path] = None) -> str:
        """Export session dialogue and plan as clean Markdown."""
        session = self.load_session(session_id)
        if not session:
            return ""

        md_lines = [
            f"# FireBox Session: {session.session_id}",
            f"**Workspace:** `{session.workspace_root}`  ",
            f"**Model:** `{session.provider} / {session.model}`  ",
            f"**Mode:** `{session.mode}`\n",
            "---",
            "## Conversation Transcript\n",
        ]

        for m in session.messages:
            role = m.get("role", "user").upper()
            content = m.get("content", "")
            md_lines.append(f"### {role}\n{content}\n")

        if session.plan:
            md_lines.append("## Mission Plan\n")
            plan_obj = ExecutionPlan(**session.plan)
            md_lines.append(plan_obj.to_markdown())

        full_md = "\n".join(md_lines)
        if output_path:
            output_path.write_text(full_md, encoding="utf-8")
        return full_md


_session_manager = None


def get_session_manager() -> SessionManager:
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
