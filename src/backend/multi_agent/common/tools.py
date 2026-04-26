from langchain_core.tools import tool

from .notebook_session import NotebookSession


def make_build_notebook_tool(session: NotebookSession):
    @tool
    def build_notebook(cells: list[dict]) -> dict:
        """Собрать ноутбук одним вызовом. cells = [{type: "markdown" | "code", content: str}, ...].
        Минимум 5 ячеек. Идемпотентный: повторный вызов сбрасывает ноутбук и собирает заново."""
        if len(cells) < 5:
            return {"error": f"build_notebook requires at least 5 cells, got {len(cells)}."}

        session.reset()
        added = []
        for c in cells:
            ctype = c.get("type")
            content = c.get("content", "")
            if ctype == "markdown":
                added.append({"index": session.add_markdown(content), "type": "markdown"})
            elif ctype == "code":
                added.append({"index": session.add_code(content), "type": "code"})
            else:
                added.append({"error": f"unknown type {ctype}"})
        return {"added": added}

    return build_notebook


def make_edit_cell_tool(session: NotebookSession):
    @tool
    def edit_cell(index: int, content: str) -> dict:
        """Заменить содержимое ячейки ноутбука целиком."""
        return session.edit_cell(index, content)

    return edit_cell


def make_delete_cell_tool(session: NotebookSession):
    @tool
    def delete_cell(index: int) -> dict:
        """Удалить ячейку из ноутбука."""
        return session.delete_cell(index)

    return delete_cell
