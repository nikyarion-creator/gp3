import json

from langchain_core.messages import HumanMessage, SystemMessage

from ..common.constants import STRUCTURED_METHOD
from ..common.llm_factory import make_supervisor_llm
from ..common.paths import agent_reports_dir, reports_dir
from ..models.final_report import FinalReport
from ..prompts.finalize import SYSTEM
from .models.finalize_output import FinalizeOutput


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


class FinalizeNode:
    def __init__(self):
        self.llm = make_supervisor_llm().with_structured_output(
            FinalizeOutput, method=STRUCTURED_METHOD
        )

    def __call__(self, state):
        de_md = read_text(agent_reports_dir("data_engineer") / "report.md")
        da_md = read_text(agent_reports_dir("data_analyst") / "report.md")
        ds_md = read_text(agent_reports_dir("data_scientist") / "report.md")

        sys = SYSTEM.format(
            business_task=state.business_task,
            target=state.target_column,
            de_report=de_md[:6000],
            da_report=da_md[:6000],
            ds_report=ds_md[:6000],
        )
        output = self.llm.invoke(
            [SystemMessage(sys), HumanMessage("Сформируй итоговый отчёт для заказчика.")]
        )

        out_dir = reports_dir() / "final"
        out_dir.mkdir(parents=True, exist_ok=True)
        md_path = out_dir / "report.md"
        json_path = out_dir / "report.json"
        md_path.write_text(output.md_report, encoding="utf-8")
        json_path.write_text(
            json.dumps(
                {
                    "business_task": state.business_task,
                    "target": state.target_column,
                    "executive_summary": output.executive_summary,
                    "key_findings": output.key_findings,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        return {
            "final_report": FinalReport(
                report_md_path=str(md_path),
                report_json_path=str(json_path),
                executive_summary=output.executive_summary,
                key_findings=output.key_findings,
            )
        }
