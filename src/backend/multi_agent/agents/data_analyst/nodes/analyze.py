from langchain_core.messages import HumanMessage, SystemMessage

from ....common.constants import STRUCTURED_METHOD
from ..models.analysis import AnalysisOutput
from ..prompts.analyze import HUMAN, SYSTEM


class AnalyzeNode:
    def __init__(self, llm, session):
        self.session = session
        self.llm = llm.with_structured_output(AnalysisOutput, method=STRUCTURED_METHOD)

    def __call__(self, state):
        sys = SYSTEM.format(business_task=state.business_task, target=state.target)
        human = HUMAN.format(notebook_snapshot=self.session.snapshot())

        out = self.llm.invoke([SystemMessage(sys), HumanMessage(human)])
        return {
            "business_insights": out.business_insights,
            "recommendations_for_ds": out.recommendations_for_ds,
            "submit_error": out.submit_error,
        }
