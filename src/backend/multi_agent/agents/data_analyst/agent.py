import json

from langgraph.graph import END, START, StateGraph

from configs.config import Config

from ...common.llm_factory import make_data_analyst_llm
from ...common.notebook_session import NotebookSession
from ...common.paths import agent_reports_dir, reports_dir
from ...common.tools import make_build_notebook_tool, make_delete_cell_tool, make_edit_cell_tool
from ...common.tools_node import ToolsNode
from ...models.common import ErrorInfo
from .conditions.route import route_after_fix, route_after_supervisor, route_after_tools
from .models.node_names import DANodeNames
from .models.state import DAState
from .nodes.analyze import AnalyzeNode
from .nodes.create_notebook import CreateNotebookNode
from .nodes.fix import FixNode
from .nodes.submit import SubmitNode
from .nodes.supervisor import SupervisorNode


class DataAnalystAgent:
    def __init__(self):
        self.config = Config()
        self.llm = make_data_analyst_llm()

    def __call__(self, state):
        iteration = max(state.da_iteration, 1)
        nb_name = (
            "data_analyst.ipynb"
            if iteration == 1
            else f"data_analyst_v{iteration}.ipynb"
        )
        session = NotebookSession(
            nb_path=reports_dir() / nb_name,
            title=f"Data Analyst (итерация {iteration})",
            figures_dir=agent_reports_dir("data_analyst") / "figures",
        )

        de_md_path = agent_reports_dir("data_engineer") / "report.md"
        de_report_md = (
            de_md_path.read_text(encoding="utf-8") if de_md_path.exists() else ""
        )
        prev_json = (
            json.dumps(state.data_analyst_report.model_dump(), ensure_ascii=False)[:4000]
            if state.data_analyst_report
            else None
        )

        da_state = DAState(
            cleaned_path=state.data_engineer_report.cleaned_dataset_path,
            md_path=str(agent_reports_dir("data_analyst") / "report.md"),
            target=state.target_column or self.config.TARGET_COLUMN,
            business_task=state.business_task or self.config.BUSINESS_TASK,
            de_report_md=de_report_md,
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

        g = StateGraph(DAState)
        g.add_node(DANodeNames.CREATE_NOTEBOOK, CreateNotebookNode(self.llm, session))
        g.add_node(DANodeNames.TOOLS, tools_node)
        g.add_node(DANodeNames.FIX, FixNode(self.llm, session))
        g.add_node(DANodeNames.ANALYZE, AnalyzeNode(self.llm, session))
        g.add_node(DANodeNames.SUPERVISOR, SupervisorNode(self.llm, session))
        g.add_node(DANodeNames.SUBMIT, SubmitNode())

        g.add_edge(START, DANodeNames.CREATE_NOTEBOOK)
        g.add_edge(DANodeNames.CREATE_NOTEBOOK, DANodeNames.TOOLS)
        g.add_conditional_edges(
            DANodeNames.TOOLS,
            route_after_tools,
            {
                DANodeNames.FIX: DANodeNames.FIX,
                DANodeNames.ANALYZE: DANodeNames.ANALYZE,
            },
        )
        g.add_conditional_edges(
            DANodeNames.FIX,
            route_after_fix,
            {
                DANodeNames.TOOLS: DANodeNames.TOOLS,
                DANodeNames.ANALYZE: DANodeNames.ANALYZE,
            },
        )
        g.add_edge(DANodeNames.ANALYZE, DANodeNames.SUPERVISOR)
        g.add_conditional_edges(
            DANodeNames.SUPERVISOR,
            route_after_supervisor,
            {
                DANodeNames.CREATE_NOTEBOOK: DANodeNames.CREATE_NOTEBOOK,
                DANodeNames.SUBMIT: DANodeNames.SUBMIT,
            },
        )
        g.add_edge(DANodeNames.SUBMIT, END)

        try:
            final = g.compile().invoke(
                da_state, config={"recursion_limit": self.config.AGENT_RECURSION_LIMIT}
            )
        except Exception as e:
            return {
                "data_analyst_report": None,
                "errors": [ErrorInfo(agent="data_analyst", message=f"{type(e).__name__}: {e}"[:500])],
            }

        report = final.get("report")
        submit_error = final.get("submit_error")
        update = {"data_analyst_report": report}
        if report is None or submit_error:
            update["data_analyst_report"] = None
            update["errors"] = [
                ErrorInfo(
                    agent="data_analyst",
                    message=submit_error or "agent finished without a report",
                )
            ]
        return update
