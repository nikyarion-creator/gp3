from operator import add
from typing import Annotated

from pydantic import BaseModel, Field

from ..agents.data_analyst.models.report import DataAnalystReport
from ..agents.data_engineer.models.report import DataEngineerReport
from ..agents.data_scientist.models.report import DataScientistReport
from .common import AgentName, ErrorInfo, PreviousBestSnapshot
from .final_report import FinalReport


class State(BaseModel):
    dataset_path: str = ""
    target_column: str = ""
    business_task: str = ""

    next_agent: AgentName | None = None
    iteration: int = 0

    data_engineer_report: DataEngineerReport | None = None
    data_analyst_report: DataAnalystReport | None = None
    data_scientist_report: DataScientistReport | None = None
    final_report: FinalReport | None = None

    de_iteration: int = 0
    da_iteration: int = 0
    ds_iteration: int = 0
    supervisor_feedback: str = ""

    previous_best: PreviousBestSnapshot | None = None

    errors: Annotated[list[ErrorInfo], add] = Field(default_factory=list)
