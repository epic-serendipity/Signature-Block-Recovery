"""Data models for signature recovery."""

from dataclasses import dataclass, field
from typing import Dict, Optional
import re


@dataclass
class Signature:
    """Represents an extracted signature block."""

    text: str
    source_msg_id: str
    timestamp: Optional[str] = None
    normalized_text: str = field(init=False)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.normalized_text = self._normalize(self.text)

    @staticmethod
    def _normalize(text: str) -> str:
        clean = re.sub(r"\s+", " ", text)
        return clean.strip().lower()


@dataclass
class Message:
    """Represents one email message extracted from a PST."""

    body: str
    msg_id: str
    timestamp: float
