#!/usr/bin/env python3
"""Tkinter GUI with search, filters, pagination and sorting."""

# Imports
import json
import logging
import os
import queue
import threading
from datetime import datetime
from functools import partial
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from ..index.search_index import SearchIndex, SQLiteFTSIndex
from ..index.indexer import index_pst
from template import log_message
from ..core.logging import setup_logging

# Logging configuration
setup_logging()

# Global state
DEFAULT_PAGE_SIZE = 10
CONFIG_PATH = (
    Path(os.getenv("APPDATA") or Path.home() / ".config")
    / "SignatureRecovery"
    / "config.json"
)


def load_user_config() -> dict | None:
    """Return config dict if available."""
    if CONFIG_PATH.is_file():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:  # pragma: no cover - defensive
            log_message("warning", f"Failed to load config: {exc}")
    return None


def save_user_config(cfg: dict) -> None:
    """Persist ``cfg`` to ``CONFIG_PATH``."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f)
    except Exception as exc:  # pragma: no cover - defensive
        log_message("error", f"Failed to save config: {exc}")


class SetupWizard(tk.Toplevel):
    """Simple first-run dialog to select PSTs and index path."""

    def __init__(self, master: tk.Misc):
        super().__init__(master)
        self.title("First-Time Setup")
        self.resizable(False, False)

        tk.Label(self, text="PST files:").grid(row=0, column=0, padx=5, pady=5)
        self.pst_var = tk.StringVar()
        tk.Entry(self, textvariable=self.pst_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self, text="Browse", command=self._choose_psts).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(self, text="Index location:").grid(row=1, column=0, padx=5, pady=5)
        self.idx_var = tk.StringVar()
        tk.Entry(self, textvariable=self.idx_var, width=40).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self, text="Browse", command=self._choose_index).grid(row=1, column=2, padx=5, pady=5)

        tk.Button(self, text="Start", command=self._finish).grid(row=2, column=1, pady=10)

        self.result = None

    def _choose_psts(self) -> None:
        files = filedialog.askopenfilenames(filetypes=[("PST files", "*.pst")])
        if files:
            self.pst_var.set(";".join(files))

    def _choose_index(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("Database", "*.db")])
        if path:
            self.idx_var.set(path)

    def _finish(self) -> None:
        psts = [p for p in self.pst_var.get().split(";") if p]
        idx = self.idx_var.get()
        if not psts or not idx:
            messagebox.showerror("Error", "Please select PST files and index path")
            return
        self.result = {"psts": psts, "index": idx}
        self.destroy()


class SearchPanel(tk.Frame):
    """Query entry and search trigger."""

    def __init__(self, master: tk.Misc, on_search) -> None:
        super().__init__(master)
        tk.Label(self, text="Search:").pack(side=tk.LEFT, padx=5)
        self.query_var = tk.StringVar()
        self.entry = tk.Entry(self, textvariable=self.query_var)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.button = tk.Button(self, text="Search", command=on_search)
        self.button.pack(side=tk.LEFT, padx=5)

    def disable(self) -> None:
        self.button.config(state=tk.DISABLED)
        self.entry.config(state=tk.DISABLED)

    def enable(self) -> None:
        self.button.config(state=tk.NORMAL)
        self.entry.config(state=tk.NORMAL)

    def get_query(self) -> str:
        return self.query_var.get().strip()


class FilterPanel(tk.LabelFrame):
    """Date range and metadata filters."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, text="Filters")
        top = tk.Frame(self)
        tk.Label(top, text="Start YYYY-MM-DD:").pack(side=tk.LEFT)
        self.start_var = tk.StringVar()
        tk.Entry(top, textvariable=self.start_var, width=12).pack(side=tk.LEFT, padx=5)
        tk.Label(top, text="End YYYY-MM-DD:").pack(side=tk.LEFT)
        self.end_var = tk.StringVar()
        tk.Entry(top, textvariable=self.end_var, width=12).pack(side=tk.LEFT, padx=5)
        top.pack(fill=tk.X, pady=2)
        lists = tk.Frame(self)
        tk.Label(lists, text="Company").pack(side=tk.LEFT)
        self.company = tk.Listbox(
            lists, selectmode=tk.MULTIPLE, height=4, exportselection=False
        )
        self.company.pack(side=tk.LEFT, padx=5)
        tk.Label(lists, text="Title").pack(side=tk.LEFT)
        self.title = tk.Listbox(
            lists, selectmode=tk.MULTIPLE, height=4, exportselection=False
        )
        self.title.pack(side=tk.LEFT, padx=5)
        lists.pack(fill=tk.X, pady=2)

        conf = tk.Frame(self)
        tk.Label(conf, text="Min Confidence:").pack(side=tk.LEFT)
        self.conf_var = tk.DoubleVar(value=0.0)
        tk.Scale(
            conf,
            variable=self.conf_var,
            from_=0.0,
            to=1.0,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            length=120,
        ).pack(side=tk.LEFT, padx=5)
        conf.pack(fill=tk.X, pady=2)

    def set_companies(self, companies) -> None:
        """Populate company filter options."""
        self.company.delete(0, tk.END)
        for c in companies:
            self.company.insert(tk.END, c)

    def set_titles(self, titles) -> None:
        """Populate title filter options."""
        self.title.delete(0, tk.END)
        for t in titles:
            self.title.insert(tk.END, t)

    def set_options(self, companies, titles) -> None:
        self.set_companies(sorted(companies))
        self.set_titles(sorted(titles))

    def get_filters(self) -> dict:
        comps = [self.company.get(i) for i in self.company.curselection()]
        titles = [self.title.get(i) for i in self.title.curselection()]
        return {
            "start": self.start_var.get().strip(),
            "end": self.end_var.get().strip(),
            "companies": comps,
            "titles": titles,
            "min_confidence": float(self.conf_var.get()),
        }


class ResultsPanel(tk.Frame):
    """Treeview display of search results."""

    def __init__(self, master: tk.Misc, on_select, on_sort) -> None:
        super().__init__(master)
        cols = ("Name", "Company", "Title", "Date", "Confidence")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=8)
        for col in cols:
            self.tree.heading(col, text=col, command=partial(on_sort, col))
            self.tree.column(col, width=100, anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", lambda e: on_select())

    def populate(self, signatures) -> None:
        self.tree.delete(*self.tree.get_children())
        for sig in signatures:
            self.tree.insert("", tk.END, values=(
                sig.metadata.name or "",
                sig.metadata.company or "",
                sig.metadata.title or "",
                sig.timestamp or "",
                f"{sig.confidence:.2f}",
            ))


class PaginationPanel(tk.Frame):
    """Prev/Next buttons and page size selector."""

    def __init__(self, master: tk.Misc, on_prev, on_next, on_size_change) -> None:
        super().__init__(master)
        self.prev_btn = tk.Button(self, text="Prev", command=on_prev)
        self.prev_btn.pack(side=tk.LEFT, padx=2)
        self.next_btn = tk.Button(self, text="Next", command=on_next)
        self.next_btn.pack(side=tk.LEFT, padx=2)
        self.size_var = tk.StringVar(value=str(DEFAULT_PAGE_SIZE))
        self.size = ttk.Combobox(
            self,
            textvariable=self.size_var,
            values=["10", "25", "50", "100"],
            width=4,
            state="readonly",
        )
        self.size.bind("<<ComboboxSelected>>", lambda e: on_size_change(int(self.size_var.get())))
        self.size.pack(side=tk.LEFT, padx=5)
        self.info = tk.Label(self, text="Page 1 of 1")
        self.info.pack(side=tk.LEFT, padx=5)

    def disable(self) -> None:
        self.prev_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.DISABLED)
        self.size.config(state="disabled")

    def enable(self) -> None:
        self.prev_btn.config(state=tk.NORMAL)
        self.next_btn.config(state=tk.NORMAL)
        self.size.config(state="readonly")

    def update_info(self, page: int, total: int) -> None:
        self.info.config(text=f"Page {page} of {total}")


class DetailPanel(tk.LabelFrame):
    """Display full signature text."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, text="Detail")
        self.text = tk.Text(self, state=tk.DISABLED, height=6)
        self.text.pack(fill=tk.BOTH, expand=True)

    def show(self, signature) -> None:
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, signature.text)
        self.text.config(state=tk.DISABLED)


class AlertsPanel(tk.LabelFrame):
    """Display recent warning/error log messages."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, text="Alerts")
        self.listbox = tk.Listbox(self, height=4)
        self.listbox.pack(fill=tk.BOTH, expand=True)

    def add_alert(self, msg: str) -> None:
        self.listbox.insert(0, msg)
        if self.listbox.size() > 100:
            self.listbox.delete(100, tk.END)


class _GuiLogHandler(logging.Handler):
    """Send warning/error logs to the GUI alerts panel."""

    def __init__(self, panel: AlertsPanel) -> None:
        super().__init__(level=logging.WARNING)
        self.panel = panel

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        try:
            self.panel.add_alert(msg)
        except Exception:
            pass


class App(tk.Tk):
    """Main Tk application."""

    def __init__(self, index: SearchIndex | None = None) -> None:
        super().__init__()
        self.title("Signature Recovery")
        self.geometry("800x600")

        self._build_menu()

        self.index = index
        cfg = None
        if self.index is None:
            cfg = load_user_config()
            if not cfg:
                wizard = SetupWizard(self)
                self.wait_window(wizard)
                cfg = wizard.result
                if cfg:
                    save_user_config(cfg)
        if cfg:
            self._start_extraction(cfg["psts"], cfg["index"])
            self.index = SQLiteFTSIndex(cfg["index"])

        self.queue: queue.Queue = queue.Queue()
        self.sort_field = "Date"
        self.sort_dir = "asc"
        self.page_size = DEFAULT_PAGE_SIZE
        self.current_page = 1
        self.results = []

        self.search_panel = SearchPanel(self, self.on_search)
        self.search_panel.pack(fill=tk.X, padx=5, pady=2)

        self.filter_panel = FilterPanel(self)
        self.filter_panel.pack(fill=tk.X, padx=5, pady=2)

        self.results_panel = ResultsPanel(self, self.select_result, self.change_sort)
        self.results_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        self.pagination_panel = PaginationPanel(self, self.prev_page, self.next_page, self.set_page_size)
        self.pagination_panel.pack(fill=tk.X, padx=5, pady=2)

        self.detail_panel = DetailPanel(self)
        self.detail_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        self.alerts_panel = AlertsPanel(self)
        self.alerts_panel.pack(fill=tk.BOTH, expand=False, padx=5, pady=2)

        handler = _GuiLogHandler(self.alerts_panel)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logging.getLogger().addHandler(handler)

        # Seed filter lists using all signatures in the index
        self._seed_filters()
        self.active = True
        self.poll_id = self.after(100, self._poll_queue)

    def close(self) -> None:
        """Shut down polling loop and destroy the window."""
        self.active = False
        if hasattr(self, "poll_id"):
            try:
                self.after_cancel(self.poll_id)
            except Exception:
                pass
        self.destroy()

    # Helpers -----------------------------------------------------------------
    def on_search(self) -> None:
        if not self.index:
            return
        raw_query = self.search_panel.query_var.get().strip()
        query = None if (raw_query == "*" or raw_query == "") else raw_query
        filters = self.filter_panel.get_filters()
        self.search_panel.disable()
        self.pagination_panel.disable()
        thread = threading.Thread(target=self._search_thread, args=(query, filters), daemon=True)
        thread.start()

    def _search_thread(self, query: str | None, filters: dict) -> None:
        log_message("info", f"Search started: {query}")
        min_conf = float(filters.get("min_confidence", 0.0))
        results = self.index.query(query, min_confidence=min_conf) if self.index else []
        results = self._apply_filters(results, filters)
        self.queue.put(results)
        log_message("info", f"Search completed: {len(results)} hits")

    def _seed_filters(self) -> None:
        """Populate filter panel using all signatures from the index."""
        if not self.index:
            return
        try:
            all_sigs = self.index.query(None)
        except Exception as exc:  # pragma: no cover - initialization guard
            log_message("error", f"Failed to seed filters: {exc}")
            return
        companies = sorted({s.metadata.company or "" for s in all_sigs})
        titles = sorted({s.metadata.title or "" for s in all_sigs})
        self.filter_panel.set_companies(companies)
        self.filter_panel.set_titles(titles)

    def _poll_queue(self) -> None:
        if not self.active:
            return
        try:
            item = self.queue.get_nowait()
        except queue.Empty:
            pass
        else:
            if isinstance(item, tuple) and item[0] == "progress":
                count, total = item[1], item[2]
                self.progress_var.set(f"Processing PST {count} of {total}...")
            elif item == "complete":
                if hasattr(self, "progress_win"):
                    self.progress_win.destroy()
                self._seed_filters()
            else:
                results = item
                self._display_results(results)
                self.search_panel.enable()
                self.pagination_panel.enable()
        self.poll_id = self.after(100, self._poll_queue)

    def _display_results(self, results) -> None:
        """Store and display search results, updating filter options."""
        self.results = results
        companies = sorted({s.metadata.company or "" for s in self.results})
        titles = sorted({s.metadata.title or "" for s in self.results})
        self.filter_panel.set_companies(companies)
        self.filter_panel.set_titles(titles)
        self.results = self._sort_results(self.results)
        self.current_page = 1
        self.show_page()

    def _apply_filters(self, results, filters):
        def in_range(ts: str) -> bool:
            if not ts:
                return True
            try:
                dt = datetime.fromisoformat(ts)
            except ValueError:
                return True
            start = filters.get("start")
            end = filters.get("end")
            if start:
                try:
                    if dt < datetime.fromisoformat(start):
                        return False
                except ValueError:
                    pass
            if end:
                try:
                    if dt > datetime.fromisoformat(end):
                        return False
                except ValueError:
                    pass
            return True

        companies = set(filters.get("companies", []))
        titles = set(filters.get("titles", []))
        out = []
        for sig in results:
            if companies and (sig.metadata.company or "") not in companies:
                continue
            if titles and (sig.metadata.title or "") not in titles:
                continue
            if not in_range(sig.timestamp or ""):
                continue
            out.append(sig)
        return out

    def _sort_results(self, results):
        key_map = {
            "Name": lambda s: s.metadata.name or "",
            "Company": lambda s: s.metadata.company or "",
            "Title": lambda s: s.metadata.title or "",
            "Date": lambda s: s.timestamp or "",
            "Confidence": lambda s: s.confidence,
        }
        reverse = self.sort_dir == "desc"
        return sorted(results, key=key_map[self.sort_field], reverse=reverse)

    def change_sort(self, field: str) -> None:
        if self.sort_field == field:
            self.sort_dir = "desc" if self.sort_dir == "asc" else "asc"
        else:
            self.sort_field = field
            self.sort_dir = "asc"
        self.results = self._sort_results(self.results)
        self.show_page()

    def set_page_size(self, size: int) -> None:
        self.page_size = size
        self.current_page = 1
        self.show_page()

    def show_page(self) -> None:
        total_pages = max(1, (len(self.results) + self.page_size - 1) // self.page_size)
        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        self.results_panel.populate(self.results[start:end])
        self.pagination_panel.update_info(self.current_page, total_pages)

    def next_page(self) -> None:
        total_pages = max(1, (len(self.results) + self.page_size - 1) // self.page_size)
        if self.current_page < total_pages:
            self.current_page += 1
            self.show_page()

    def prev_page(self) -> None:
        if self.current_page > 1:
            self.current_page -= 1
            self.show_page()

    def select_result(self) -> None:
        items = self.results_panel.tree.selection()
        if not items:
            return
        idx = self.results_panel.tree.index(items[0])
        global_index = (self.current_page - 1) * self.page_size + idx
        if 0 <= global_index < len(self.results):
            self.detail_panel.show(self.results[global_index])

    # Menu and extraction -----------------------------------------------------
    def _build_menu(self) -> None:
        menu = tk.Menu(self)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="New Extraction", command=self._new_extraction)
        file_menu.add_command(label="Open Index", command=self._open_index)
        menu.add_cascade(label="File", menu=file_menu)
        self.config(menu=menu)

    def _new_extraction(self) -> None:
        wizard = SetupWizard(self)
        self.wait_window(wizard)
        cfg = wizard.result
        if not cfg:
            return
        save_user_config(cfg)
        self._start_extraction(cfg["psts"], cfg["index"])
        self.index = SQLiteFTSIndex(cfg["index"])
        self._seed_filters()

    def _open_index(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Database", "*.db")])
        if path:
            self.index = SQLiteFTSIndex(path)
            self._seed_filters()

    def _start_extraction(self, pst_files, index_path) -> None:
        self.progress_win = tk.Toplevel(self)
        self.progress_win.title("Extracting")
        self.progress_var = tk.StringVar(value="Starting...")
        tk.Label(self.progress_win, textvariable=self.progress_var).pack(padx=10, pady=10)
        thread = threading.Thread(target=self._extract_thread, args=(pst_files, index_path), daemon=True)
        thread.start()

    def _extract_thread(self, pst_files, index_path) -> None:
        index = SQLiteFTSIndex(index_path)
        total = len(pst_files)
        for i, pst in enumerate(pst_files, 1):
            index_pst(pst, index)
            self.queue.put(("progress", i, total))
        self.queue.put("complete")


def main() -> None:
    index = SQLiteFTSIndex("signatures.db")
    app = App(index)
    app.mainloop()


if __name__ == "__main__":
    main()
