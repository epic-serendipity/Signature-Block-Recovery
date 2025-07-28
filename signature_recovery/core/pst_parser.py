#!/usr/bin/env python3
"""
pst_parser.py
-------------
PSTParser streams email messages out of a .pst file, yielding
Message objects with body, msg_id, and timestamp.
"""

import os
import logging
import time
from typing import Iterator, List, Optional

from signature_recovery.core.models import Message
from template import log_message  # our helper
from .logging import retry

logger = logging.getLogger("PSTParser")
logger.setLevel(logging.INFO)


class PSTParser:
    """Abstraction over a PST file. Yields Message instances."""

    def __init__(self, pst_path: str) -> None:
        """Initialize with path to the PST file."""
        if not os.path.isfile(pst_path):
            log_message("error", f"PST file not found: {pst_path}")
            raise FileNotFoundError(f"PST file not found: {pst_path}")

        try:
            import pypff
        except ImportError as e:
            log_message("critical", "pypff library is required for PST parsing")
            raise

        self._pst = pypff.file()
        self._open(pst_path)
        log_message("info", f"Opened PST file: {pst_path}")

    @retry(Exception, tries=3, delay=0.5)
    def _open(self, path: str) -> None:
        """Open PST file with retries."""
        try:
            self._pst.open(path)
        except Exception:
            log_message("error", f"Failed to open PST: {path}", component="pst_parser")
            raise

    def iter_messages(
        self,
        folders: Optional[List[str]] = None,
        start: Optional[float] = None,
        end: Optional[float] = None,
    ) -> Iterator[Message]:
        """Traverse folders and yield ``Message`` objects.

        Parameters
        ----------
        folders:
            Optional list of folder names to include. If ``None`` all folders are
            processed.
        start:
            Optional epoch timestamp; messages older than this are skipped.
        end:
            Optional epoch timestamp; messages newer than this are skipped.
        """
        root = self._pst.get_root_folder()
        for folder in self._walk_folders(root):
            if folders and folder.name not in folders:
                continue
            for i in range(folder.get_number_of_sub_messages()):
                try:
                    item = folder.get_sub_message(i)
                    timestamp = getattr(item, "client_submit_time", None) or time.time()
                    if start and timestamp < start:
                        continue
                    if end and timestamp > end:
                        continue
                    body = item.plain_text_body or item.html_body or ""
                    msg_id = (
                        item.identifier.hex()
                        if hasattr(item, "identifier")
                        else str(time.time())
                    )
                    yield Message(body=body, msg_id=msg_id, timestamp=timestamp)
                except Exception as e:
                    log_message(
                        "warning",
                        f"Failed to read message #{i} in folder {folder.name}: {e}",
                        component="pst_parser",
                        msg_id=f"{folder.name}/{i}",
                    )
                    continue

    def _walk_folders(self, folder) -> Iterator:
        """Recursively walk subfolders."""
        yield folder
        for i in range(folder.get_number_of_sub_folders()):
            sub = folder.get_sub_folder(i)
            yield from self._walk_folders(sub)


def main() -> None:
    """Quick test harness."""
    import argparse

    parser = argparse.ArgumentParser(description="Test PSTParser")
    parser.add_argument("pst_file", help="Path to PST file")
    args = parser.parse_args()
    parser_obj = PSTParser(args.pst_file)
    count = 0
    for msg in parser_obj.iter_messages():
        print(f"{msg.msg_id} @ {msg.timestamp}")
        count += 1
        if count >= 5:
            break


if __name__ == "__main__":
    main()
