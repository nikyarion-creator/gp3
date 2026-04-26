from langchain_core.messages import HumanMessage, SystemMessage

from ....common.constants import STRUCTURED_METHOD
from ....common.tools import make_build_notebook_tool
from ..models.plan import Plan
from ..prompts.create_notebook import HUMAN_INIT, HUMAN_QC, HUMAN_RETRY, SYSTEM


class CreateNotebookNode:
    def __init__(self, llm, session):
        self.llm = llm.with_structured_output(Plan, method=STRUCTURED_METHOD)
        self.build_notebook = make_build_notebook_tool(session)

    def __call__(self, state):
        sys = SYSTEM.format(
            cleaned_path=state.cleaned_path,
            feature_dataset_path=state.feature_dataset_path,
            model_path=state.model_path,
            metrics_path=state.metrics_path,
            target=state.target,
            business_task=state.business_task,
            de_report=state.de_report_md[:3000],
            da_report=state.da_report_md[:3000],
            da_recommendations=state.da_recommendations[:1500],
        )

        if state.cycle > 0:
            human = HUMAN_QC.format(
                qc_round=state.cycle + 1,
                qc_feedback=state.qc_feedback or "(нет фидбека)",
            )
        elif state.iteration > 1 and state.prev_report_json:
            human = HUMAN_RETRY.format(
                iteration=state.iteration,
                supervisor_feedback=state.supervisor_feedback or "(без фидбека)",
                prev_report_json=state.prev_report_json,
            )
        else:
            human = HUMAN_INIT.format(cleaned_path=state.cleaned_path)

        plan = self.llm.invoke([SystemMessage(sys), HumanMessage(human)])
        self.build_notebook.invoke({"cells": [c.model_dump() for c in plan.cells]})

        return {
            "plan": plan,
            "fix_attempts": 0,
            "tune_done": False,
            "results": [],
            "submit_error": None,
        }
