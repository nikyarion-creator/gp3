from typing import Any, Optional

from pydantic import BaseModel, Field

from .plan import Plan
from .report import DataScientistReport


class DSState(BaseModel):
    cleaned_path: str
    feature_dataset_path: str
    model_path: str
    metrics_path: str
    md_path: str
    target: str
    business_task: str
    de_report_md: str = ""
    da_report_md: str = ""
    da_recommendations: str = ""
    iteration: int = 1
    supervisor_feedback: Optional[str] = None
    prev_report_json: Optional[str] = None

    plan: Optional[Plan] = None
    results: list[dict] = Field(default_factory=list)
    fix_attempts: int = 0
    tune_done: bool = False

    should_tune: bool = False
    tune_reasoning: str = ""

    cycle: int = 0
    approved: bool = False
    qc_feedback: str = ""

    submit_error: Optional[str] = None

    validated_metrics: dict[str, float] = Field(default_factory=dict)
    best_model_name: Optional[str] = None

    last_ai_message: Optional[Any] = None
    last_tool_caller: Optional[str] = None

    report: Optional[DataScientistReport] = None
