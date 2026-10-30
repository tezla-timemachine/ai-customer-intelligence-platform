"""Optional AI step — suggest product opportunities from the top pain points (FR-13).

Input is the code-computed ranking plus real quotes, so suggestions are grounded.
Output is always labelled 'AI suggestion'; the PM decides what, if anything, to act on.
"""
from __future__ import annotations

import json
import re

import pandas as pd

from . import llm
from .aggregate import evidence

PROMPT = """You are helping a Product Manager for a {domain}.
Below are the top customer pain points, ranked by code from real reviews, each with real quotes.

{pain_points}

Suggest up to 5 product opportunities. Each must address one listed pain point and be specific
enough for a team to scope. Do not invent facts beyond the quotes.
Return ONLY a JSON array: [{{"pain_point": "<category>", "opportunity": "<one sentence>", "why": "<one sentence citing the quotes>"}}]"""


def suggest(df: pd.DataFrame, ranked: pd.DataFrame, domain: str, top: int = 5) -> list[dict]:
    blocks = []
    for r in ranked.head(top).itertuples():
        quotes = evidence(df, r.category, n=3)["feedback"].str.slice(0, 200).tolist()
        blocks.append(f"- {r.category} ({int(r.negative + r.mixed)} complaints)\n" + "\n".join(f'  "{q}"' for q in quotes))
    if not blocks:
        return []
    if llm.provider() == "mock":
        return [{"pain_point": r.category, "opportunity": f"Investigate and reduce '{r.top_theme}' issues.",
                 "why": "Mock suggestion — run with a real LLM provider for genuine output."}
                for r in ranked.head(top).itertuples()]
    raw = llm.complete(PROMPT.format(domain=domain, pain_points="\n".join(blocks)))
    m = re.search(r"\[.*\]", raw, re.S)
    try:
        items = json.loads(m.group(0)) if m else []
    except json.JSONDecodeError:
        return []
    valid = set(ranked["category"])
    return [i for i in items if isinstance(i, dict) and i.get("pain_point") in valid][:top]
