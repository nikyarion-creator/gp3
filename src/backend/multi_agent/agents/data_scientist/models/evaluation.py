from typing import Optional

from pydantic import BaseModel, Field


class EvaluationOutput(BaseModel):
    should_tune: bool = Field(
        description="True если метрики слабые/неоптимальные и стоит запустить tune-цикл."
    )
    reasoning: str = Field(
        description="Почему именно так решили (что в метриках смотрели, на какие критерии опирались)."
    )
    submit_error: Optional[str] = Field(
        default=None,
        description=(
            "Если работу нельзя сабмитить (упали ячейки, best_metrics.json не записан, "
            "нет ключевых метрик f1/precision/recall/roc_auc, модель не сохранена) - "
            "сюда КОНКРЕТНОЕ описание проблемы. Если всё ок - оставь None."
        ),
    )
