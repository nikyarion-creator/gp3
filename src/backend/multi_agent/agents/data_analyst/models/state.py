from typing import Any, Optional

from pydantic import BaseModel, Field

from .plan import Plan
from .report import DataAnalystReport


class DAState(BaseModel):
    cleaned_path: str
    md_path: str
    target: str
    business_task: str
    de_report_md: str = ""
    iteration: int = 1
    supervisor_feedback: Optional[str] = None
    prev_report_json: Optional[str] = None

    plan: Optional[Plan] = None
    results: list[dict] = Field(default_factory=list)
    fix_attempts: int = 0

    business_insights: list[str] = Field(default_factory=list)
    recommendations_for_ds: list[str] = Field(default_factory=list)

    cycle: int = 0
    approved: bool = False
    qc_feedback: str = ""

    submit_error: Optional[str] = None

    # Буфер для tool-calls между LLM-нодой и TOOLS-нодой.
    # LLM-нода (fix) кладёт сюда AIMessage. TOOLS читает tool_calls, исполняет, обнуляет.
    last_ai_message: Optional[Any] = None
    last_tool_caller: Optional[str] = None

    report: Optional[DataAnalystReport] = None
