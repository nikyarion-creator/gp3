from ..models.node_names import DENodeNames


MAX_QC_CYCLES = 2


def route_after_tools(state):
    if any(not r["ok"] for r in state.results):
        return DENodeNames.FIX
    return DENodeNames.SUPERVISOR


def route_after_fix(state):
    last = state.last_ai_message
    if last and getattr(last, "tool_calls", None):
        return DENodeNames.TOOLS
    return DENodeNames.SUPERVISOR


def route_after_supervisor(state):
    if state.approved or state.cycle >= MAX_QC_CYCLES:
        return DENodeNames.SUBMIT
    return DENodeNames.CREATE_NOTEBOOK
