import time
import tkinter as tk
from pyvirtualdisplay import Display
import pytest

from signature_recovery.gui.app import App
from signature_recovery.index.search_index import SQLiteFTSIndex
from signature_recovery.core.models import Signature, SignatureMetadata


@pytest.fixture(scope="module")
def display():
    """Provide a shared virtual display for GUI tests."""
    with Display():
        yield


def _build_index(tmp_path):
    db = tmp_path / "idx.db"
    idx = SQLiteFTSIndex(str(db))
    sigs = [
        Signature(
            text="John Doe\nEngineer",
            source_msg_id="1",
            timestamp="2021-01-01",
            metadata=SignatureMetadata(name="John Doe", company="ACME", title="Engineer"),
            confidence=0.9,
        ),
        Signature(
            text="Jane Smith\nManager",
            source_msg_id="2",
            timestamp="2021-01-02",
            metadata=SignatureMetadata(name="Jane Smith", company="Beta", title="Manager"),
            confidence=0.8,
        ),
        Signature(
            text="Bob\nEngineer",
            source_msg_id="3",
            timestamp="2021-01-03",
            metadata=SignatureMetadata(name="Bob", company="ACME", title="Engineer"),
            confidence=0.7,
        ),
    ]
    idx.add_batch(sigs)
    return idx


def test_app_instantiation(tmp_path, display):
    idx = _build_index(tmp_path)
    app = App(idx)
    app.update()
    assert isinstance(app.search_panel.entry, tk.Entry)
    app.close()


def test_search_and_pagination(tmp_path, display):
    idx = _build_index(tmp_path)
    app = App(idx)
    app.page_size = 2
    app.search_panel.query_var.set("*")
    app.start_search()
    for _ in range(20):
        app.update()
        if app.results:
            break
        time.sleep(0.05)
    assert len(app.results) == 3
    first_page = [app.results_panel.tree.item(i)["values"][0] for i in app.results_panel.tree.get_children()]
    assert len(first_page) == 2
    app.next_page()
    app.update()
    second_page = [app.results_panel.tree.item(i)["values"][0] for i in app.results_panel.tree.get_children()]
    assert second_page and second_page[0] != first_page[0]
    app.close()


def test_filtering_and_sort(tmp_path, display):
    idx = _build_index(tmp_path)
    app = App(idx)
    app.search_panel.query_var.set("*")
    app.start_search()
    for _ in range(20):
        app.update()
        if app.results:
            break
        time.sleep(0.05)
    acme_index = app.filter_panel.company.get(0, tk.END).index("ACME")
    app.filter_panel.company.selection_set(acme_index)
    app.start_search()
    for _ in range(20):
        app.update()
        if len(app.results) <= 2:
            break
        time.sleep(0.05)
    assert all(r.metadata.company == "ACME" for r in app.results)
    app.change_sort("Name")
    app.change_sort("Name")
    names = [r.metadata.name for r in app.results]
    assert names == sorted(names, reverse=True)
    app.close()
