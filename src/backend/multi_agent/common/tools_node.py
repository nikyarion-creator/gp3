class ToolsNode:
    def __init__(self, session, tools):
        self.session = session
        self.tools_by_name = {t.name: t for t in tools}

    def __call__(self, state):
        last = state.last_ai_message
        tool_calls = getattr(last, "tool_calls", None) or [] if last else []

        for tc in tool_calls:
            tool = self.tools_by_name.get(tc["name"])
            if tool is None:
                continue
            try:
                tool.invoke(tc["args"])
            except Exception:
                pass

        return {
            "results": self.session.execute_all(),
            "last_ai_message": None,
        }
