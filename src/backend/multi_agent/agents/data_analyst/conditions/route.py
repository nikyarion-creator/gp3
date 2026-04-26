from ..models.node_names import DANodeNames


MAX_QC_CYCLES = 2


def route_after_tools(state):
    if any(not r["ok"] for r in state.results):
        return DANodeNames.FIX
    return DANodeNames.ANALYZE


def route_after_fix(state):
    last = state.last_ai_message
    if last and getattr(last, "tool_calls", None):
        return DANodeNames.TOOLS
    return DANodeNames.ANALYZE


def route_after_supervisor(state):
    if state.approved or state.cycle >= MAX_QC_CYCLES:
        return DANodeNames.SUBMIT
    return DANodeNames.CREATE_NOTEBOOK
