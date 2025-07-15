"""Data models for signature recovery."""

from dataclasses import dataclass, field
from typing import Optional
import re


@dataclass
class SignatureMetadata:
    """Structured metadata extracted from a signature."""

    name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    url: Optional[str] = None
    address: Optional[str] = None


@dataclass
class Signature:
    """Represents an extracted signature block."""

    text: str
    source_msg_id: str
    timestamp: Optional[str] = None
    normalized_text: str = field(init=False)
    metadata: SignatureMetadata = field(default_factory=SignatureMetadata)

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
