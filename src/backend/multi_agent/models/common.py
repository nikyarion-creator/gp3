from typing import Literal

from pydantic import BaseModel


AgentName = Literal[
    "data_engineer",
    "data_analyst",
    "data_scientist",
    "finish",
]


class ErrorInfo(BaseModel):
    agent: str
    message: str


class PreviousBestSnapshot(BaseModel):
    model_name: str
    metrics: dict[str, float]
    saved_at: str
    feature_columns: list[str]
