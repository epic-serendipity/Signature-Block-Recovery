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
logger = logging.getLogger(__name__)
from .logging import retry

try:
    import pypff
except ImportError:  # pragma: no cover - optional dependency
    pypff = None

logger = logging.getLogger("PSTParser")
logger.setLevel(logging.INFO)


class PSTParser:
    """Abstraction over a PST file. Yields Message instances."""

    def __init__(self, pst_path: str) -> None:
        """Initialize with path to the PST file."""
        if not os.path.isfile(pst_path):
            logger.error("PST file not found: %s", pst_path)
            raise FileNotFoundError(f"PST file not found: {pst_path}")

        if pypff is None:
            try:
                import importlib

                pypff_module = importlib.import_module("pypff")
                globals()["pypff"] = pypff_module
            except ImportError as e:  # pragma: no cover - dependency missing
                raise RuntimeError(
                    "PST parsing requires the optional pypff library. "
                    "Install it via `pip install signature-recovery[pst]`, "
                    "or see docs for building pypff."
                ) from e

        self._pst = pypff.file()
        self._open(pst_path)
        logger.info("Opened PST file: %s", pst_path)

    @retry(Exception, tries=3, delay=0.5)
    def _open(self, path: str) -> None:
        """Open PST file with retries."""
        try:
            self._pst.open(path)
        except Exception:
            logger.error(
                "Failed to open PST: %s",
                path,
                extra={"component": "pst_parser"},
            )
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
                    logger.warning(
                        "Failed to read message #%s in folder %s: %s",
                        i,
                        folder.name,
                        e,
                        extra={
                            "component": "pst_parser",
                            "msg_id": f"{folder.name}/{i}",
                        },
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
