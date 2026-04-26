from langchain_core.messages import HumanMessage, SystemMessage

from ....common.tools import make_edit_cell_tool
from ..prompts.tune import HUMAN, SYSTEM


class TuneNode:
    def __init__(self, llm, session):
        self.session = session
        self.llm = llm.bind_tools([make_edit_cell_tool(session)])

    def __call__(self, state):
        human = HUMAN.format(
            best_model_name=state.best_model_name or "(нет)",
            validated_metrics=state.validated_metrics or "(нет)",
            tune_reasoning=state.tune_reasoning or "(нет)",
            metrics_path=state.metrics_path,
            model_path=state.model_path,
            notebook_snapshot=self.session.snapshot(),
        )
        response = self.llm.invoke([SystemMessage(SYSTEM), HumanMessage(human)])
        return {
            "last_ai_message": response,
            "last_tool_caller": "tune",
            "tune_done": True,
        }
