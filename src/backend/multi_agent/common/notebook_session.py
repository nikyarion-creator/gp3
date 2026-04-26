import contextlib
import io
import json
import traceback

import nbformat


def _parse_outputs(cell, stdout_limit, stderr_limit):
    stdout_parts = []
    stderr_parts = []
    n_figs = 0
    ok = True

    for o in getattr(cell, "outputs", []) or []:
        otype = o.get("output_type")
        if otype == "stream":
            text = o.get("text", "")
            if isinstance(text, list):
                text = "".join(text)
            if o.get("name") == "stderr":
                stderr_parts.append(text)
                ok = False
            else:
                stdout_parts.append(text)
        elif otype == "display_data":
            n_figs += 1
        elif otype == "error":
            ok = False
            stderr_parts.append("\n".join(o.get("traceback", [])) or o.get("evalue", ""))

    stdout = "".join(stdout_parts).strip()[:stdout_limit]
    stderr = "".join(stderr_parts).strip()[:stderr_limit]
    return ok, stdout, stderr, n_figs


class NotebookSession:
    def __init__(self, nb_path, title, figures_dir=None):
        self.nb_path = nb_path
        self.figures_dir = figures_dir
        self.title = title
        self.ns = {"__name__": "__main__"}
        self.nb = nbformat.v4.new_notebook()
        self.nb.cells.append(nbformat.v4.new_markdown_cell(f"# {title}"))
        self._save()

    def reset(self):
        self.ns = {"__name__": "__main__"}
        self.nb = nbformat.v4.new_notebook()
        self.nb.cells.append(nbformat.v4.new_markdown_cell(f"# {self.title}"))
        self._save()

    def add_markdown(self, text):
        self.nb.cells.append(nbformat.v4.new_markdown_cell(text))
        self._save()
        return len(self.nb.cells) - 1

    def add_code(self, code):
        self.nb.cells.append(nbformat.v4.new_code_cell(code))
        self._save()
        return len(self.nb.cells) - 1

    def edit_cell(self, index, content):
        self.nb.cells[index].source = content
        self.nb.cells[index].outputs = []
        self._save()
        return {"index": index}

    def delete_cell(self, index):
        self.nb.cells.pop(index)
        self._save()
        return {"deleted_index": index}

    def snapshot(self, stdout_limit=1500, stderr_limit=1500):
        if not self.nb.cells:
            return "(ноутбук пуст)"

        parts = []
        for i, cell in enumerate(self.nb.cells):
            parts.append(f"## [{i}] {cell.cell_type}")
            parts.append(f"source:\n{cell.source}")

            if cell.cell_type == "code":
                ok, stdout, stderr, n_figs = _parse_outputs(cell, stdout_limit, stderr_limit)
                parts.append(f"ok={ok}, n_figs={n_figs}")
                if stdout:
                    parts.append(f"stdout:\n{stdout}")
                if stderr:
                    parts.append(f"stderr:\n{stderr}")
            parts.append("")

        return "\n".join(parts)

    def execute_all(self):
        self.ns = {"__name__": "__main__"}
        results = []
        fig_n = 0

        for i, cell in enumerate(self.nb.cells):
            if cell.cell_type != "code":
                continue

            buf = io.StringIO()
            ok = True
            try:
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                    exec(cell.source, self.ns)
            except Exception:
                ok = False
                buf.write(traceback.format_exc())
            text = buf.getvalue()

            cell.outputs = []
            if text:
                cell.outputs.append(nbformat.v4.new_output(
                    "stream", name="stdout" if ok else "stderr", text=text,
                ))

            figs = list(self.ns.get("FIGS", [])) if ok else []
            if "FIGS" in self.ns:
                self.ns["FIGS"] = []
            for fig in figs:
                cell.outputs.append(nbformat.v4.new_output(
                    "display_data",
                    data={"application/vnd.plotly.v1+json": json.loads(fig.to_json())},
                ))
                if self.figures_dir:
                    self.figures_dir.mkdir(parents=True, exist_ok=True)
                    fig_n += 1
                    fig.write_html(str(self.figures_dir / f"fig_{fig_n:03d}.html"), include_plotlyjs="cdn")

            results.append({
                "cell_index": i,
                "ok": ok,
                "stdout": text if ok else "",
                "stderr": text if not ok else "",
                "n_figs": len(figs),
            })
            if not ok:
                break

        self._save()
        return results

    def _save(self):
        self.nb_path.parent.mkdir(parents=True, exist_ok=True)
        nbformat.write(self.nb, str(self.nb_path))
