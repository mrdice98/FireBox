"""
Task Planner & Milestone Tracker for FireBox.
Generates, updates, and persists step-by-step living plans for autonomous agents.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import time
import json


class PlanStep(BaseModel):
    id: int
    title: str
    status: str = "pending"   # "pending", "in_progress", "done", "failed"
    subtasks: List[Dict[str, str]] = Field(default_factory=list)
    result_summary: Optional[str] = None


class ExecutionPlan(BaseModel):
    title: str = "FireBox Mission Plan"
    goal: str = ""
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    steps: List[PlanStep] = Field(default_factory=list)

    def add_step(self, title: str, subtasks: Optional[List[str]] = None) -> PlanStep:
        step_id = len(self.steps) + 1
        sub_list = [{"text": s, "status": "pending"} for s in (subtasks or [])]
        step = PlanStep(id=step_id, title=title, subtasks=sub_list)
        self.steps.append(step)
        self.updated_at = time.time()
        return step

    def mark_step(self, step_id: int, status: str, summary: Optional[str] = None):
        for s in self.steps:
            if s.id == step_id:
                s.status = status
                if summary:
                    s.result_summary = summary
                self.updated_at = time.time()
                break

    def get_current_step(self) -> Optional[PlanStep]:
        for s in self.steps:
            if s.status in ("in_progress", "pending"):
                return s
        return None

    def is_complete(self) -> bool:
        if not self.steps:
            return False
        return all(s.status == "done" for s in self.steps)

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", f"**Goal:** {self.goal}\n"]
        for s in self.steps:
            mark = "x" if s.status == "done" else " "
            lines.append(f"- [{mark}] **Step {s.id}:** {s.title} `({s.status})`")
            for sub in s.subtasks:
                sub_mark = "x" if sub.get("status") == "done" else " "
                lines.append(f"  - [{sub_mark}] {sub.get('text', '')}")
            if s.result_summary:
                lines.append(f"    *Result:* {s.result_summary}")
        return "\n".join(lines)
