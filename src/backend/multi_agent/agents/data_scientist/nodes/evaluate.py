import json
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from ....common.constants import STRUCTURED_METHOD
from ..models.evaluation import EvaluationOutput
from ..prompts.evaluate import HUMAN, SYSTEM


class EvaluateNode:
    def __init__(self, llm, session):
        self.session = session
        self.llm = llm.with_structured_output(EvaluationOutput, method=STRUCTURED_METHOD)

    def __call__(self, state):
        metrics_path = Path(state.metrics_path)
        metrics = {}
        if metrics_path.exists():
            try:
                metrics = json.loads(metrics_path.read_text(encoding="utf-8")) or {}
                metrics_summary = json.dumps(metrics, ensure_ascii=False, indent=2)
            except Exception as e:
                metrics_summary = f"(метрики не парсятся: {e!r})"
        else:
            metrics_summary = "(метрики не записаны)"

        sys = SYSTEM.format(business_task=state.business_task, target=state.target)
        human = HUMAN.format(
            metrics_summary=metrics_summary,
            tune_done=state.tune_done,
            notebook_snapshot=self.session.snapshot(),
        )

        evaluation = self.llm.invoke([SystemMessage(sys), HumanMessage(human)])

        update = {
            "should_tune": evaluation.should_tune,
            "tune_reasoning": evaluation.reasoning,
            "submit_error": evaluation.submit_error,
        }
        if not evaluation.submit_error:
            tm = (metrics or {}).get("test_metrics") or {}
            update["validated_metrics"] = {str(k): float(v) for k, v in tm.items()}
            update["best_model_name"] = str(metrics.get("model_name") or "unknown")
        return update
