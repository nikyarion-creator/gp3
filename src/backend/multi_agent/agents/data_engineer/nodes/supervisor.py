from langchain_core.messages import HumanMessage, SystemMessage

from ....common.constants import STRUCTURED_METHOD
from ..models.supervisor_decision import SupervisorDecision
from ..prompts.supervisor import HUMAN, SYSTEM


class SupervisorNode:
    def __init__(self, llm, session):
        self.session = session
        self.llm = llm.with_structured_output(SupervisorDecision, method=STRUCTURED_METHOD)

    def __call__(self, state):
        sys = SYSTEM.format(business_task=state.business_task, target=state.target)
        human = HUMAN.format(
            qc_round=state.cycle + 1,
            target=state.target,
            md_report_excerpt=state.plan.md_report[:1500] if state.plan else "",
            notebook_snapshot=self.session.snapshot(),
        )
        decision = self.llm.invoke([SystemMessage(sys), HumanMessage(human)])
        return {
            "approved": decision.approved,
            "qc_feedback": decision.feedback,
            "cycle": state.cycle + 1,
        }
