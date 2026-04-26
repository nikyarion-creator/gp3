from typing import Optional

from pydantic import BaseModel, Field


class AnalysisOutput(BaseModel):
    business_insights: list[str] = Field(default_factory=list)
    recommendations_for_ds: list[str] = Field(default_factory=list)
    submit_error: Optional[str] = Field(
        default=None,
        description=(
            "Если работу нельзя сабмитить (упали ячейки, мало графиков, EDA дырявый, "
            "не выполнены бизнес-требования) - сюда КОНКРЕТНОЕ описание проблемы. "
            "Если EDA полный и пригоден к сабмиту - оставь None."
        ),
    )
