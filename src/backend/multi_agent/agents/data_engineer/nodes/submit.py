from pathlib import Path

from ..models.report import DataEngineerReport


class SubmitNode:
    def __call__(self, state):
        if state.submit_error:
            return {"report": None}

        md = Path(state.md_path)
        md.parent.mkdir(parents=True, exist_ok=True)
        md.write_text(state.plan.md_report, encoding="utf-8")

        report = DataEngineerReport(
            cleaned_dataset_path=state.out_path,
            report_md_path=str(md),
        )
        return {"report": report}
