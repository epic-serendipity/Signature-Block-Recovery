#!/usr/bin/env python3
"""Minimal Tkinter GUI for signature recovery."""

import threading
import tkinter as tk
from tkinter import filedialog

from ..index.indexer import index_pst
from ..index.search_index import SQLiteFTSIndex


class SignatureApp(tk.Tk):
    """Simple GUI using Tkinter."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Signature Recovery")
        self.geometry("500x400")

        self.start_btn = tk.Button(self, text="Start Extraction", command=self.start)
        self.start_btn.pack(pady=10)
        self.log_text = tk.Text(self, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def start(self) -> None:
        pst_path = filedialog.askopenfilename(title="Select PST")
        if not pst_path:
            return
        self.start_btn.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.run_extraction, args=(pst_path,), daemon=True)
        thread.start()

    def run_extraction(self, pst_path: str) -> None:
        index = SQLiteFTSIndex("signatures.db")
        index_pst(pst_path, index)
        self.start_btn.config(state=tk.NORMAL)


def main() -> None:
    app = SignatureApp()
    app.mainloop()


if __name__ == "__main__":
    main()
