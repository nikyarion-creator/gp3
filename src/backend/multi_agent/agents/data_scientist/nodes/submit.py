from pathlib import Path

from ..models.report import BestModel, DataScientistReport


class SubmitNode:
    def __call__(self, state):
        if state.submit_error:
            return {"report": None}

        md = Path(state.md_path)
        md.parent.mkdir(parents=True, exist_ok=True)
        md.write_text(state.plan.md_report, encoding="utf-8")

        report = DataScientistReport(
            report_md_path=str(md),
            feature_dataset_path=state.feature_dataset_path,
            best_model=BestModel(
                model_name=state.best_model_name or "unknown",
                test_metrics=state.validated_metrics or {},
            ),
            best_model_path=state.model_path,
        )
        return {"report": report}
