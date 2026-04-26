from pydantic import BaseModel, Field

from ...models.common import AgentName


class SupervisorDecision(BaseModel):
    reasoning: str = Field(description="THOUGHT по текущему состоянию (CoT)")
    next_agent: AgentName = Field(description="ACTION: какого агента вызвать")
    instruction: str = Field(
        default="",
        description=(
            "Только при retry: конкретный фидбек агенту, что именно переделать. "
            "На обычном forward-вызове - пустая строка."
        ),
    )
