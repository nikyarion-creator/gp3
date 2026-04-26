from ..models.node_names import DSNodeNames


MAX_QC_CYCLES = 2


def route_after_tools(state):
    if any(not r["ok"] for r in state.results):
        return DSNodeNames.FIX
    return DSNodeNames.EVALUATE


def route_after_fix(state):
    last = state.last_ai_message
    if last and getattr(last, "tool_calls", None):
        return DSNodeNames.TOOLS
    return DSNodeNames.EVALUATE


def route_after_evaluate(state):
    if state.should_tune and not state.tune_done:
        return DSNodeNames.TUNE
    return DSNodeNames.SUPERVISOR


def route_after_tune(state):
    last = state.last_ai_message
    if last and getattr(last, "tool_calls", None):
        return DSNodeNames.TOOLS
    return DSNodeNames.EVALUATE


def route_after_supervisor(state):
    if state.approved or state.cycle >= MAX_QC_CYCLES:
        return DSNodeNames.SUBMIT
    return DSNodeNames.CREATE_NOTEBOOK
