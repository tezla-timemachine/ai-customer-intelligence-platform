"""Step 2 — Clean & redact personal data before any LLM call (deterministic code). FR-03, D10."""
from __future__ import annotations

import re

PATTERNS = [
    ("[EMAIL]", re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")),
    # UK sort code e.g. 09-01-28 or 09 01 28
    ("[SORT CODE]", re.compile(r"\b\d{2}[- ]\d{2}[- ]\d{2}\b")),
    # UK phone numbers: +44 or 0 followed by 9-10 digits with optional spaces
    ("[PHONE]", re.compile(r"(?:\+44\s?|\b0)(?:\d\s?){9,10}\b")),
    # card / account numbers: 8+ digits, optionally spaced or dashed in groups
    ("[NUMBER]", re.compile(r"\b(?:\d[ -]?){8,19}\b")),
]


def redact(text: str) -> str:
    out = text
    for token, pattern in PATTERNS:
        out = pattern.sub(token, out)
    return re.sub(r"\s+", " ", out).strip()
