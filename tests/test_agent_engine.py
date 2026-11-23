"""
Tests for Agent Engine, Planning, Modes, Context, and Sessions.
"""

import pytest
from pathlib import Path
from firebox.agent.modes import AgentMode
from firebox.agent.planner import ExecutionPlan
from firebox.agent.context import ContextManager
from firebox.agent.session import SessionManager
from firebox.agent.engine import AgentEngine
from firebox.providers.registry import get_provider_registry
from firebox.providers.base import ChatMessage


def test_planner():
    plan = ExecutionPlan(title="Build API", goal="Create user endpoints")
    s1 = plan.add_step("Setup schema", subtasks=["Define User", "Define Token"])
    s2 = plan.add_step("Implement routes")

    assert len(plan.steps) == 2
    assert plan.is_complete() is False

    plan.mark_step(1, "done", summary="Schemas defined")
    assert plan.steps[0].status == "done"
    assert "Schemas defined" in plan.to_markdown()


def test_context_manager(tmp_path):
    (tmp_path / "FIREBOX.md").write_text("# Project Custom Rule: Always use tabs", encoding="utf-8")
    ctx = ContextManager(tmp_path)

    instructions = ctx.load_project_instructions()
    assert "Always use tabs" in instructions

    sys_prompt = ctx.build_system_prompt(AgentMode.BUILD)
    assert "ACTIVE MODE: BUILD" in sys_prompt
    assert "Always use tabs" in sys_prompt


def test_session_manager(tmp_path):
    sm = SessionManager(tmp_path / "sessions")
    messages = [
        ChatMessage(role="user", content="Hello"),
        ChatMessage(role="assistant", content="Hi there!"),
    ]
    path = sm.save_session(
        session_id="test_sess_1",
        workspace_root=tmp_path,
        messages=messages,
        mode=AgentMode.AUTONOMOUS,
    )
    assert path.exists()

    loaded = sm.load_session("test_sess_1")
    assert loaded is not None
    assert len(loaded.messages) == 2

    sessions = sm.list_sessions()
    assert len(sessions) == 1
    assert sessions[0]["session_id"] == "test_sess_1"

    md = sm.export_session_markdown("test_sess_1")
    assert "### USER\nHello" in md


def test_agent_engine_autonomous_loop(tmp_path):
    # Configure mock provider
    reg = get_provider_registry()
    reg.set_active_provider("mock", model="firebox-sim-1.0")

    engine = AgentEngine(workspace_root=tmp_path, session_id="auto_test", mode=AgentMode.AUTONOMOUS)
    
    # Create test file to read
    (tmp_path / "test.txt").write_text("Secret content 12345", encoding="utf-8")

    # Run agent turn
    response = engine.run_turn("Please read test.txt")
    assert response != ""
    assert len(engine.messages) >= 3
