#!/usr/bin/env python3
"""Minimal Tkinter GUI for signature recovery."""

import threading
import tkinter as tk
from tkinter import filedialog

from ..index.indexer import index_pst
from ..index.search_index import SQLiteFTSIndex
from template import log_message


class SignatureApp(tk.Tk):
    """Simple GUI using Tkinter."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Signature Recovery")
        self.geometry("500x400")

        # extraction controls
        self.start_btn = tk.Button(self, text="Start Extraction", command=self.start)
        self.start_btn.pack(pady=10)

        # search controls
        self.search_frame = tk.Frame(self)
        tk.Label(self.search_frame, text="Search Signatures:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_btn = tk.Button(self.search_frame, text="Search", command=self.start_search)
        self.search_btn.pack(side=tk.LEFT)
        self.search_frame.pack(fill=tk.X, padx=10, pady=5)

        self.results_list = tk.Listbox(self, height=6)
        self.results_list.pack(fill=tk.BOTH, expand=True, padx=10)
        self.results_list.bind("<<ListboxSelect>>", self.show_signature)

        self.sig_text = tk.Text(self, height=6, state=tk.DISABLED)
        self.sig_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_text = tk.Text(self, height=8)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.index: SQLiteFTSIndex | None = None
        self._results = []

    def start(self) -> None:
        pst_path = filedialog.askopenfilename(title="Select PST")
        if not pst_path:
            return
        self.start_btn.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.run_extraction, args=(pst_path,), daemon=True)
        thread.start()

    def run_extraction(self, pst_path: str) -> None:
        self.index = SQLiteFTSIndex("signatures.db")
        index_pst(pst_path, self.index)
        self.start_btn.config(state=tk.NORMAL)

    def start_search(self) -> None:
        if not self.index:
            return
        query = self.search_var.get().strip()
        if not query:
            return
        self.search_btn.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.run_search, args=(query,), daemon=True)
        thread.start()

    def run_search(self, query: str) -> None:
        log_message("info", f"Search started: {query}")
        results = self.index.query(query) if self.index else []
        log_message("info", f"Search completed: {len(results)} hits")
        self._results = results
        self.after(0, self.populate_results)

    def populate_results(self) -> None:
        self.results_list.delete(0, tk.END)
        for sig in self._results:
            first = sig.text.splitlines()[0] if sig.text else ""
            label = f"{first} ({sig.timestamp})"
            self.results_list.insert(tk.END, label)
        self.search_btn.config(state=tk.NORMAL)

    def show_signature(self, event: tk.Event) -> None:
        if not self.results_list.curselection():
            return
        idx = self.results_list.curselection()[0]
        sig = self._results[idx]
        self.sig_text.config(state=tk.NORMAL)
        self.sig_text.delete("1.0", tk.END)
        self.sig_text.insert(tk.END, sig.text)
        self.sig_text.config(state=tk.DISABLED)


def main() -> None:
    app = SignatureApp()
    app.mainloop()


if __name__ == "__main__":
    main()
