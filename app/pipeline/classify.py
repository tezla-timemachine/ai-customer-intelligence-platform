"""Steps 3–5 — Batching, LLM classification, structured-output check (D3, D6, D9).

The LLM only labels text. Every object it returns is validated with Pydantic;
a bad batch is retried once, then its rows are marked 'Unclassified'.
No row is ever silently dropped.

Batches are sent in parallel (CR-12), up to LLM_MAX_CONCURRENCY at a time
(default 5). Each batch is still independent: a failure affects only its rows.
"""
from __future__ import annotations

import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Literal, Optional

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator

from . import llm

ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_PATH = ROOT / "config" / "taxonomy.yaml"
PROMPT_PATH = ROOT / "prompts" / "classify_v3.txt"  # v3: main issue chosen by outcome (the task that went wrong)
PROMPT_VERSION = PROMPT_PATH.stem
BATCH_SIZE = 20
UNCLASSIFIED = "Unclassified"


def max_concurrency() -> int:
    """How many batches to send at once (CR-12). 1 restores one-at-a-time."""
    try:
        return max(1, int(os.getenv("LLM_MAX_CONCURRENCY", "5")))
    except ValueError:
        return 5


def load_taxonomy(path: Path = TAXONOMY_PATH) -> dict:
    return yaml.safe_load(path.read_text())


class Label(BaseModel):
    id: str
    category: str
    other_categories: list[str] = Field(default_factory=list)
    sentiment: Literal["positive", "negative", "neutral", "mixed"]
    theme: str = Field(max_length=120)
    problem: Optional[str] = None
    confidence: float = Field(ge=0, le=1)

    @field_validator("id", mode="before")
    @classmethod
    def _id_str(cls, v):
        return str(v)


def build_prompt(batch: list[tuple[str, str]], taxonomy: dict) -> str:
    cats = "\n".join(f"- {c['name']}: {c['definition']} Example: \"{c['example']}\"" for c in taxonomy["categories"])
    sents = "\n".join(f"- {s['name']}: {s['definition']}" for s in taxonomy["sentiments"])
    reviews = "\n".join(f"{rid}: {text}" for rid, text in batch)
    return PROMPT_PATH.read_text().format(domain=taxonomy["domain"], categories=cats, sentiments=sents, reviews=reviews)


def _extract_json(text: str):
    """Models sometimes wrap JSON in prose or ``` fences — take the outermost array."""
    m = re.search(r"\[.*\]", text, re.S)
    if not m:
        raise ValueError("No JSON array in response")
    return json.loads(m.group(0))


def parse_and_check(raw: str, batch_ids: list[str], allowed: set[str]) -> dict[str, Label]:
    """Return valid labels keyed by id (may be fewer than the batch). Raises if no JSON at all."""
    items = _extract_json(raw)
    labels: dict[str, Label] = {}
    for item in items:
        try:
            lab = Label(**item)
        except ValidationError:
            continue
        if lab.category not in allowed or lab.id not in batch_ids or lab.id in labels:
            continue
        # keep only valid, distinct secondary categories (never the main one), max 3
        seen, others = {lab.category}, []
        for c in lab.other_categories:
            if c in allowed and c not in seen:
                seen.add(c); others.append(c)
        lab.other_categories = others[:3]
        labels[lab.id] = lab
    return labels


@dataclass
class RunStats:
    provider: str = ""
    model: str = ""
    prompt_version: str = PROMPT_VERSION
    batches: int = 0
    retries: int = 0
    unclassified: int = 0
    seconds: float = 0.0
    errors: list[str] = field(default_factory=list)


def classify(rows: list[tuple[str, str]], taxonomy: dict | None = None,
             progress: Callable[[float], None] | None = None) -> tuple[dict[str, dict], RunStats]:
    """rows: list of (id, redacted_text). Returns {id: label dict} for every input id."""
    taxonomy = taxonomy or load_taxonomy()
    allowed = {c["name"] for c in taxonomy["categories"]}
    stats = RunStats(provider=llm.provider(), model=llm.model_name())
    start = time.time()
    results: dict[str, dict] = {}
    batches = [rows[i:i + BATCH_SIZE] for i in range(0, len(rows), BATCH_SIZE)]

    # Build every prompt (and the audit log) up front, in order, before any call is made.
    jobs = []
    for n, batch in enumerate(batches, 1):
        ids = [str(r[0]) for r in batch]
        prompt = build_prompt([(str(i), t) for i, t in batch], taxonomy)
        if os.getenv("LOG_PROMPTS") == "1":  # audit trail: exactly what was sent to the LLM (UAT-21)
            with open(ROOT / "data" / "prompt_log.txt", "a") as fh:
                fh.write(f"\n===== batch {n} =====\n{prompt}\n")
        jobs.append((n, ids, prompt))

    def run_batch(n: int, ids: list[str], prompt: str):
        """One batch, retried once. Runs in a worker thread, so it only returns data."""
        labels: dict[str, Label] = {}
        errors: list[str] = []
        retried = False
        for attempt in (1, 2):
            try:
                got = parse_and_check(llm.complete(prompt), ids, allowed)
                labels.update({k: v for k, v in got.items() if k not in labels})
            except Exception as exc:  # bad JSON or API error
                errors.append(f"batch {n} attempt {attempt}: {exc}")
            if len(labels) == len(ids):
                break
            if attempt == 1:
                retried = True  # some rows missing/invalid -> retry the batch once
        return labels, errors, retried

    # Send batches in parallel (CR-12); progress is reported here, on the caller's thread.
    outcomes: dict[int, tuple] = {}
    with ThreadPoolExecutor(max_workers=min(max_concurrency(), max(1, len(jobs)))) as pool:
        futures = {pool.submit(run_batch, n, ids, prompt): n for n, ids, prompt in jobs}
        for done, fut in enumerate(as_completed(futures), 1):
            outcomes[futures[fut]] = fut.result()
            if progress:
                progress(done / len(jobs))

    # Assemble in the original batch order, so results never depend on timing.
    for n, ids, _ in jobs:
        labels, errors, retried = outcomes[n]
        stats.errors.extend(errors)
        stats.retries += int(retried)
        for rid in ids:
            if labels and rid in labels:
                d = labels[rid].model_dump()
                d["other_categories"] = "; ".join(d["other_categories"])  # flat string: easy to store, filter and export
                results[rid] = d
            else:
                stats.unclassified += 1
                results[rid] = {"id": rid, "category": UNCLASSIFIED, "other_categories": "", "sentiment": None,
                                "theme": None, "problem": None, "confidence": 0.0}
    stats.batches = len(jobs)
    stats.seconds = round(time.time() - start, 1)
    return results, stats
