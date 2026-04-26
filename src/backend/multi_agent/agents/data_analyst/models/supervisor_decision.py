from pydantic import BaseModel, Field


class SupervisorDecision(BaseModel):
    approved: bool = Field(description="True если EDA приемлем, False если нужна ещё итерация.")
    feedback: str = Field(
        default="",
        description="Если approved=False - конкретный фидбек что улучшить (1-3 предложения).",
    )
