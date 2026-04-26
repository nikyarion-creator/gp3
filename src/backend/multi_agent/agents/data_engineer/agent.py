import json

from langgraph.graph import END, START, StateGraph

from configs.config import Config

from ...common.llm_factory import make_data_engineer_llm
from ...common.notebook_session import NotebookSession
from ...common.paths import agent_reports_dir, dataset_path, processed_dir, reports_dir
from ...common.tools import make_build_notebook_tool, make_delete_cell_tool, make_edit_cell_tool
from ...common.tools_node import ToolsNode
from ...models.common import ErrorInfo
from .conditions.route import route_after_fix, route_after_supervisor, route_after_tools
from .models.node_names import DENodeNames
from .models.state import DEState
from .nodes.create_notebook import CreateNotebookNode
from .nodes.fix import FixNode
from .nodes.submit import SubmitNode
from .nodes.supervisor import SupervisorNode


class DataEngineerAgent:
    def __init__(self):
        self.config = Config()
        self.llm = make_data_engineer_llm()

    def __call__(self, state):
        iteration = max(state.de_iteration, 1)
        nb_name = (
            "data_engineer.ipynb"
            if iteration == 1
            else f"data_engineer_v{iteration}.ipynb"
        )
        session = NotebookSession(
            nb_path=reports_dir() / nb_name,
            title=f"Data Engineer (итерация {iteration})",
        )

        prev_json = (
            json.dumps(state.data_engineer_report.model_dump(), ensure_ascii=False)[:4000]
            if state.data_engineer_report
            else None
        )
        de_state = DEState(
            raw_path=state.dataset_path or str(dataset_path()),
            out_path=str(processed_dir() / "cleaned.csv"),
            md_path=str(agent_reports_dir("data_engineer") / "report.md"),
            target=state.target_column or self.config.TARGET_COLUMN,
            business_task=state.business_task or self.config.BUSINESS_TASK,
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

        g = StateGraph(DEState)
        g.add_node(DENodeNames.CREATE_NOTEBOOK, CreateNotebookNode(self.llm, session))
        g.add_node(DENodeNames.TOOLS, tools_node)
        g.add_node(DENodeNames.FIX, FixNode(self.llm, session))
        g.add_node(DENodeNames.SUPERVISOR, SupervisorNode(self.llm, session))
        g.add_node(DENodeNames.SUBMIT, SubmitNode())

        g.add_edge(START, DENodeNames.CREATE_NOTEBOOK)
        g.add_edge(DENodeNames.CREATE_NOTEBOOK, DENodeNames.TOOLS)
        g.add_conditional_edges(
            DENodeNames.TOOLS,
            route_after_tools,
            {
                DENodeNames.FIX: DENodeNames.FIX,
                DENodeNames.SUPERVISOR: DENodeNames.SUPERVISOR,
            },
        )
        g.add_conditional_edges(
            DENodeNames.FIX,
            route_after_fix,
            {
                DENodeNames.TOOLS: DENodeNames.TOOLS,
                DENodeNames.SUPERVISOR: DENodeNames.SUPERVISOR,
            },
        )
        g.add_conditional_edges(
            DENodeNames.SUPERVISOR,
            route_after_supervisor,
            {
                DENodeNames.CREATE_NOTEBOOK: DENodeNames.CREATE_NOTEBOOK,
                DENodeNames.SUBMIT: DENodeNames.SUBMIT,
            },
        )
        g.add_edge(DENodeNames.SUBMIT, END)

        try:
            final = g.compile().invoke(
                de_state, config={"recursion_limit": self.config.AGENT_RECURSION_LIMIT}
            )
        except Exception as e:
            return {
                "data_engineer_report": None,
                "errors": [ErrorInfo(agent="data_engineer", message=f"{type(e).__name__}: {e}"[:500])],
            }

        report = final.get("report")
        submit_error = final.get("submit_error")
        update = {"data_engineer_report": report}
        if report is None or submit_error:
            update["data_engineer_report"] = None
            update["errors"] = [
                ErrorInfo(
                    agent="data_engineer",
                    message=submit_error or "agent finished without a report",
                )
            ]
        return update
