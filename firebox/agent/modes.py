"""
Agent Execution Modes for FireBox.
Ask, Plan, Build, Autonomous, and Review modes.
"""

from enum import Enum
from typing import Dict, Any


class AgentMode(str, Enum):
    ASK = "ask"                 # Read-only explanation and Q&A, no file writes
    PLAN = "plan"               # Multi-step strategic planning without executing mutations
    BUILD = "build"             # Direct implementation of code and plans with verification
    AUTONOMOUS = "autonomous"   # End-to-end loop: inspect -> plan -> execute -> test -> iterate
    REVIEW = "review"           # Deep code review for bugs, security, maintainability, tests


MODE_DESCRIPTIONS: Dict[AgentMode, str] = {
    AgentMode.ASK: "Explain and answer questions without modifying any files.",
    AgentMode.PLAN: "Analyze codebase and design a detailed milestone plan without making changes.",
    AgentMode.BUILD: "Implement code changes, refactors, and features directly.",
    AgentMode.AUTONOMOUS: "Full autonomous loop: analyze, plan, edit, run tests, diagnose, and iterate.",
    AgentMode.REVIEW: "Perform deep code review analyzing architecture, security, performance, and bugs.",
}
