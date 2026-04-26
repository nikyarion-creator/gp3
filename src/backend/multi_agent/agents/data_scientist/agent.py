import json

from langgraph.graph import END, START, StateGraph

from configs.config import Config

from ...common.llm_factory import make_data_scientist_llm
from ...common.notebook_session import NotebookSession
from ...common.paths import agent_reports_dir, memory_dir, processed_dir, reports_dir
from ...common.tools import make_build_notebook_tool, make_delete_cell_tool, make_edit_cell_tool
from ...common.tools_node import ToolsNode
from ...models.common import ErrorInfo
from .conditions.route import (
    route_after_evaluate,
    route_after_fix,
    route_after_supervisor,
    route_after_tools,
    route_after_tune,
)
from .models.node_names import DSNodeNames
from .models.state import DSState
from .nodes.create_notebook import CreateNotebookNode
from .nodes.evaluate import EvaluateNode
from .nodes.fix import FixNode
from .nodes.submit import SubmitNode
from .nodes.supervisor import SupervisorNode
from .nodes.tune import TuneNode


class DataScientistAgent:
    def __init__(self):
        self.config = Config()
        self.llm = make_data_scientist_llm()

    def __call__(self, state):
        iteration = max(state.ds_iteration, 1)
        nb_name = (
            "data_scientist.ipynb"
            if iteration == 1
            else f"data_scientist_v{iteration}.ipynb"
        )
        session = NotebookSession(
            nb_path=reports_dir() / nb_name,
            title=f"Data Scientist (итерация {iteration})",
            figures_dir=agent_reports_dir("data_scientist") / "figures",
        )

        de_md_path = agent_reports_dir("data_engineer") / "report.md"
        da_md_path = agent_reports_dir("data_analyst") / "report.md"
        de_report_md = de_md_path.read_text(encoding="utf-8") if de_md_path.exists() else ""
        da_report_md = da_md_path.read_text(encoding="utf-8") if da_md_path.exists() else ""
        da_recs = "\n".join(f"- {r}" for r in state.data_analyst_report.recommendations_for_ds)

        prev_json = (
            json.dumps(state.data_scientist_report.model_dump(), ensure_ascii=False)[:4000]
            if state.data_scientist_report
            else None
        )

        ds_state = DSState(
            cleaned_path=state.data_engineer_report.cleaned_dataset_path,
            feature_dataset_path=str(processed_dir() / "features.csv"),
            model_path=str(memory_dir() / "best_model.pkl"),
            metrics_path=str(memory_dir() / "best_metrics.json"),
            md_path=str(agent_reports_dir("data_scientist") / "report.md"),
            target=state.target_column or self.config.TARGET_COLUMN,
            business_task=state.business_task or self.config.BUSINESS_TASK,
            de_report_md=de_report_md,
            da_report_md=da_report_md,
            da_recommendations=da_recs,
            iteration=iteration,
            supervisor_feedback=state.supervisor_feedback,
            prev_report_json=prev_json,
        )

        tools_node = ToolsNode(
            session,
            tools=[
                make_build_notebook_tool(session),
                make_edit_cell_tool(session),
                make_delete_cell_tool(session),
            ],
        )

        g = StateGraph(DSState)
        g.add_node(DSNodeNames.CREATE_NOTEBOOK, CreateNotebookNode(self.llm, session))
        g.add_node(DSNodeNames.TOOLS, tools_node)
        g.add_node(DSNodeNames.FIX, FixNode(self.llm, session))
        g.add_node(DSNodeNames.EVALUATE, EvaluateNode(self.llm, session))
        g.add_node(DSNodeNames.TUNE, TuneNode(self.llm, session))
        g.add_node(DSNodeNames.SUPERVISOR, SupervisorNode(self.llm, session))
        g.add_node(DSNodeNames.SUBMIT, SubmitNode())

        g.add_edge(START, DSNodeNames.CREATE_NOTEBOOK)
        g.add_edge(DSNodeNames.CREATE_NOTEBOOK, DSNodeNames.TOOLS)
        g.add_conditional_edges(
            DSNodeNames.TOOLS,
            route_after_tools,
            {
                DSNodeNames.FIX: DSNodeNames.FIX,
                DSNodeNames.EVALUATE: DSNodeNames.EVALUATE,
            },
        )
        g.add_conditional_edges(
            DSNodeNames.FIX,
            route_after_fix,
            {
                DSNodeNames.TOOLS: DSNodeNames.TOOLS,
                DSNodeNames.EVALUATE: DSNodeNames.EVALUATE,
            },
        )
        g.add_conditional_edges(
            DSNodeNames.EVALUATE,
            route_after_evaluate,
            {
                DSNodeNames.TUNE: DSNodeNames.TUNE,
                DSNodeNames.SUPERVISOR: DSNodeNames.SUPERVISOR,
            },
        )
        g.add_conditional_edges(
            DSNodeNames.TUNE,
            route_after_tune,
            {
                DSNodeNames.TOOLS: DSNodeNames.TOOLS,
                DSNodeNames.EVALUATE: DSNodeNames.EVALUATE,
            },
        )
        g.add_conditional_edges(
            DSNodeNames.SUPERVISOR,
            route_after_supervisor,
            {
                DSNodeNames.CREATE_NOTEBOOK: DSNodeNames.CREATE_NOTEBOOK,
                DSNodeNames.SUBMIT: DSNodeNames.SUBMIT,
            },
        )
        g.add_edge(DSNodeNames.SUBMIT, END)

        try:
            final = g.compile().invoke(
                ds_state, config={"recursion_limit": self.config.AGENT_RECURSION_LIMIT}
            )
        except Exception as e:
            return {
                "data_scientist_report": None,
                "errors": [ErrorInfo(agent="data_scientist", message=f"{type(e).__name__}: {e}"[:500])],
            }

        report = final.get("report")
        submit_error = final.get("submit_error")
        update = {"data_scientist_report": report}
        if report is None or submit_error:
            update["data_scientist_report"] = None
            update["errors"] = [
                ErrorInfo(
                    agent="data_scientist",
                    message=submit_error or "agent finished without a report",
                )
            ]
        return update
