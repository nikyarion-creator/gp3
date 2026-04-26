from typing import Any, Optional

from pydantic import BaseModel, Field

from .plan import Plan
from .report import DataEngineerReport


class DEState(BaseModel):
    raw_path: str
    out_path: str
    md_path: str
    target: str
    business_task: str
    iteration: int = 1
    supervisor_feedback: Optional[str] = None
    prev_report_json: Optional[str] = None

    plan: Optional[Plan] = None
    results: list[dict] = Field(default_factory=list)
    fix_attempts: int = 0

    cycle: int = 0
    approved: bool = False
    qc_feedback: str = ""

    submit_error: Optional[str] = None

    last_ai_message: Optional[Any] = None
    last_tool_caller: Optional[str] = None

    report: Optional[DataEngineerReport] = None
