#!/usr/bin/env python3
"""Tkinter GUI with search, filters, pagination and sorting."""

# Imports
import logging
import queue
import threading
from datetime import datetime
from functools import partial
import tkinter as tk
from tkinter import ttk

from ..index.search_index import SearchIndex, SQLiteFTSIndex
from template import log_message

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Global state
DEFAULT_PAGE_SIZE = 10


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
        self.company = tk.Listbox(lists, selectmode=tk.MULTIPLE, height=4, exportselection=False)
        self.company.pack(side=tk.LEFT, padx=5)
        tk.Label(lists, text="Title").pack(side=tk.LEFT)
        self.title = tk.Listbox(lists, selectmode=tk.MULTIPLE, height=4, exportselection=False)
        self.title.pack(side=tk.LEFT, padx=5)
        lists.pack(fill=tk.X, pady=2)

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


class App(tk.Tk):
    """Main Tk application."""

    def __init__(self, index: SearchIndex | None = None) -> None:
        super().__init__()
        self.title("Signature Recovery")
        self.geometry("800x600")

        self.index = index
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
        query = self.search_panel.get_query() or "*"
        filters = self.filter_panel.get_filters()
        self.search_panel.disable()
        self.pagination_panel.disable()
        thread = threading.Thread(target=self._search_thread, args=(query, filters), daemon=True)
        thread.start()

    def _search_thread(self, query: str, filters: dict) -> None:
        log_message("info", f"Search started: {query}")
        results = self.index.query(query) if self.index else []
        results = self._apply_filters(results, filters)
        self.queue.put(results)
        log_message("info", f"Search completed: {len(results)} hits")

    def _poll_queue(self) -> None:
        if not self.active:
            return
        try:
            results = self.queue.get_nowait()
        except queue.Empty:
            pass
        else:
            self._process_results(results)
            self.search_panel.enable()
            self.pagination_panel.enable()
        self.poll_id = self.after(100, self._poll_queue)

    def _process_results(self, results) -> None:
        self.results = self._sort_results(results)
        companies = sorted({s.metadata.company or "" for s in results})
        titles = sorted({s.metadata.title or "" for s in results})
        self.filter_panel.set_companies(companies)
        self.filter_panel.set_titles(titles)
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


def main() -> None:
    index = SQLiteFTSIndex("signatures.db")
    app = App(index)
    app.mainloop()


if __name__ == "__main__":
    main()
