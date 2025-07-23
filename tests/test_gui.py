import time
import tkinter as tk
from pyvirtualdisplay import Display
import pytest

from signature_recovery.gui.app import App
from signature_recovery.index.search_index import SearchIndex, SQLiteFTSIndex
from signature_recovery.core.models import Signature, SignatureMetadata


class DummyIndex(SearchIndex):
    """Simple in-memory index for tests."""

    def __init__(self, results):
        self._results = results

    def add(self, signature: Signature) -> None:  # pragma: no cover - not used
        pass

    def query(self, q: str, **kwargs):
        return self._results


@pytest.fixture(scope="module")
def display():
    with Display():
        yield


def _build_index(tmp_path, count=3):
    db = tmp_path / "idx.db"
    idx = SQLiteFTSIndex(str(db))
    sigs = [
        Signature(
            text=f"User {i}",
            source_msg_id=str(i),
            timestamp=f"2021-01-0{i}",
            metadata=SignatureMetadata(name=f"User {i}", company="ACME", title="Engineer"),
            confidence=0.9 - i * 0.1,
        )
        for i in range(1, count + 1)
    ]
    idx.add_batch(sigs)
    return idx


def test_app_instantiation(tmp_path, display):
    idx = _build_index(tmp_path)
    app = App(idx)
    app.update()
    assert isinstance(app.search_panel.entry, tk.Entry)
    app.close()


def test_search_results(tmp_path, display):
    sig = Signature(text="A", source_msg_id="1", metadata=SignatureMetadata())
    idx = DummyIndex([sig])
    app = App(idx)
    app.search_panel.query_var.set("*")
    app.on_search()
    for _ in range(20):
        app.update()
        if app.results:
            break
        time.sleep(0.05)
    rows = app.results_panel.tree.get_children()
    assert len(rows) == 1
    app.close()


def test_pagination_next(tmp_path, display):
    idx = _build_index(tmp_path, count=5)
    app = App(idx)
    app.set_page_size(2)
    app.search_panel.query_var.set("*")
    app.on_search()
    for _ in range(20):
        app.update()
        if app.results:
            break
        time.sleep(0.05)
    first = [app.results_panel.tree.item(i)["values"][0] for i in app.results_panel.tree.get_children()]
    app.next_page()
    app.update()
    second = [app.results_panel.tree.item(i)["values"][0] for i in app.results_panel.tree.get_children()]
    assert second and second[0] != first[0]
    app.close()


def test_filter_company(tmp_path, display):
    idx = _build_index(tmp_path)
    app = App(idx)
    app.search_panel.query_var.set("*")
    app.on_search()
    for _ in range(20):
        app.update()
        if app.results:
            break
        time.sleep(0.05)
    comp_index = app.filter_panel.company.get(0, tk.END).index("ACME")
    app.filter_panel.company.selection_set(comp_index)
    app.on_search()
    for _ in range(20):
        app.update()
        if app.results:
            break
        time.sleep(0.05)
    assert all(r.metadata.company == "ACME" for r in app.results)
    app.close()


def test_sort_toggle(tmp_path, display):
    idx = _build_index(tmp_path)
    app = App(idx)
    app.search_panel.query_var.set("*")
    app.on_search()
    for _ in range(20):
        app.update()
        if app.results:
            break
        time.sleep(0.05)
    app.change_sort("Name")
    app.change_sort("Name")
    names = [r.metadata.name for r in app.results]
    assert names == sorted(names, reverse=True)
    app.close()
