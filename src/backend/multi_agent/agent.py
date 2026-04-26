import json
from datetime import datetime, timezone

from configs.config import Config

from .common.paths import memory_dir
from .graph import MultiAgentGraph
from .models.common import ErrorInfo, PreviousBestSnapshot
from .models.state import State


class MultiAgent:
    def __init__(self):
        self.config = Config()
        self.graph = MultiAgentGraph().graph

    def __call__(self, text=None):
        init_state = State(
            dataset_path=self.config.DATASET_PATH,
            target_column=self.config.TARGET_COLUMN,
            business_task=self.config.BUSINESS_TASK,
            previous_best=_load_previous_best(),
        )
        try:
            final = self.graph.invoke(
                init_state, config={"recursion_limit": self.config.MAIN_RECURSION_LIMIT}
            )
            return State.model_validate(final)
        except Exception as e:
            return init_state.model_copy(update={
                "errors": [ErrorInfo(agent="pipeline", message=str(e))]
            })


def _load_previous_best():
    snap = memory_dir() / "best_metrics.json"
    if not snap.exists():
        return None
    raw = json.loads(snap.read_text())
    return PreviousBestSnapshot(
        model_name=raw.get("model_name", "unknown"),
        metrics=raw.get("metrics", {}),
        saved_at=raw.get("saved_at", datetime.now(timezone.utc).isoformat()),
        feature_columns=raw.get("feature_columns", []),
    )
