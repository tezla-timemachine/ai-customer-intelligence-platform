"""Orchestrates the pipeline: validate → redact → classify → (aggregate in the UI) → store."""
from __future__ import annotations

from dataclasses import asdict

import pandas as pd

from . import classify, llm, storage
from .redact import redact
from .validate import validate


def analyse(raw: bytes, filename: str, progress=None, use_cache: bool = True):
    """Return (labelled DataFrame, validation report, run stats dict, from_cache flag)."""
    df, report = validate(raw, filename)
    fhash = storage.file_hash(raw, llm.provider(), llm.model_name(), classify.PROMPT_VERSION)
    if use_cache:
        cached = storage.find_run(fhash)
        if cached is not None:
            return cached, report, {"provider": llm.provider(), "model": llm.model_name(), "cached": True}, True

    df["id"] = df["id"].astype(str)
    rows = [(rid, redact(text)) for rid, text in zip(df["id"], df["feedback"])]
    labels, stats = classify.classify(rows, progress=progress)
    lab = pd.DataFrame(labels.values())
    out = df.merge(lab, on="id", how="left")
    stats_d = asdict(stats)
    if stats.unclassified < len(out):  # never cache a run where the AI failed completely
        storage.save_run(out, fhash, filename, stats_d)
    return out, report, stats_d, False
