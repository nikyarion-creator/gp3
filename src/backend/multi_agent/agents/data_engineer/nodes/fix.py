from langchain_core.messages import HumanMessage, SystemMessage

from ....common.tools import make_edit_cell_tool
from ..prompts.fix import HUMAN, SYSTEM


class FixNode:
    def __init__(self, llm, session):
        self.session = session
        self.llm = llm.bind_tools([make_edit_cell_tool(session)])

    def __call__(self, state):
        human = HUMAN.format(notebook_snapshot=self.session.snapshot())
        response = self.llm.invoke([SystemMessage(SYSTEM), HumanMessage(human)])
        return {
            "last_ai_message": response,
            "last_tool_caller": "fix",
            "fix_attempts": state.fix_attempts + 1,
        }
