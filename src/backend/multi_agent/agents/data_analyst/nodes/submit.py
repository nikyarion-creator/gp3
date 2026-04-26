from pathlib import Path

from pydantic import ValidationError

from ..models.report import DataAnalystReport


class SubmitNode:
    def __call__(self, state):
        if state.submit_error:
            return {"report": None}

        md = Path(state.md_path)
        md.parent.mkdir(parents=True, exist_ok=True)
        md.write_text(state.plan.md_report, encoding="utf-8")

        try:
            report = DataAnalystReport(
                report_md_path=str(md),
                business_insights=state.business_insights,
                recommendations_for_ds=state.recommendations_for_ds,
            )
        except ValidationError as e:
            return {
                "report": None,
                "submit_error": f"SubmitNode (DA): pydantic-валидация: {e!r}",
            }
        return {"report": report}
