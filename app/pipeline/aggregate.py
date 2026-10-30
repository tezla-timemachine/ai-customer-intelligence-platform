"""Step 6 — Aggregation (deterministic code). FR-08, FR-09, FR-10, D2, D11.

Everything here is plain pandas: counts, percentages, ranking and quote
selection. No LLM is involved, so the numbers are exact and repeatable.
"""
from __future__ import annotations

import pandas as pd

PROBLEM_SENTIMENTS = ("negative", "mixed")
NON_ISSUE = ("Praise", "Unclassified", "Other")  # "Other" is shown separately as a taxonomy-health signal


def by_column(df: pd.DataFrame, col: str) -> pd.DataFrame:
    out = df[col].fillna("Unclassified").value_counts().rename_axis(col).reset_index(name="count")
    out["pct"] = (out["count"] / len(df) * 100).round(1)
    return out


def mentions(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (review, category raised): the main category plus any other_categories.

    A review that complains about login AND slow loading counts once for each (D7 v2).
    `is_main` marks the review's main issue.
    """
    main = df.assign(mention=df["category"], is_main=True)
    others = df.get("other_categories")
    if others is None:
        return main
    sec = df.assign(mention=others.fillna("").astype(str).str.split(";")).explode("mention")
    sec["mention"] = sec["mention"].str.strip()
    sec = sec[sec["mention"] != ""].assign(is_main=False)
    return pd.concat([main, sec], ignore_index=True)


def pain_points(df: pd.DataFrame, top: int = 10) -> pd.DataFrame:
    """Rank categories by negative/mixed mentions (the ranking rule, FR-09).

    Counts every issue a customer raised — main or secondary — because each is a real complaint.
    Score = negative mentions + 0.5 × mixed mentions (a mixed review is half a complaint).
    Ties are broken by average star rating (lower = worse).
    """
    m = mentions(df)
    probs = m[m["sentiment"].isin(PROBLEM_SENTIMENTS) & ~m["mention"].isin(NON_ISSUE)]
    cols = ["category", "negative", "mixed", "as_main_issue", "score", "pct_of_all", "avg_rating", "top_theme"]
    if probs.empty:
        return pd.DataFrame(columns=cols)
    g = probs.groupby("mention").agg(
        negative=("sentiment", lambda s: (s == "negative").sum()),
        mixed=("sentiment", lambda s: (s == "mixed").sum()),
        as_main_issue=("is_main", "sum"),
        avg_rating=("rating", "mean"),
        top_theme=("theme", lambda s: s.dropna().str.lower().value_counts().index[0] if s.notna().any() else ""),
    ).reset_index().rename(columns={"mention": "category"})
    g["score"] = g["negative"] + 0.5 * g["mixed"]
    g["pct_of_all"] = ((g["negative"] + g["mixed"]) / len(df) * 100).round(1)
    g["avg_rating"] = g["avg_rating"].round(2)
    return g.sort_values(["score", "avg_rating"], ascending=[False, True]).head(top).reset_index(drop=True)[cols]


def evidence(df: pd.DataFrame, category: str, n: int = 5) -> pd.DataFrame:
    """Real quotes for a pain point, looked up by row — never generated (D11).

    Reviews where it is the main issue come first, then high confidence, then longer text.
    """
    m = mentions(df)
    sub = m[(m["mention"] == category) & m["sentiment"].isin(PROBLEM_SENTIMENTS)].copy()
    sub["_len"] = sub["feedback"].str.len().clip(upper=400)
    sub = sub.sort_values(["is_main", "confidence", "_len"], ascending=False).drop_duplicates("id")
    return sub[["id", "date", "rating", "segment", "feedback", "theme", "is_main"]].head(n)


def monthly(df: pd.DataFrame) -> pd.DataFrame:
    m = df.assign(month=df["date"].dt.to_period("M").astype(str))
    return m.groupby("month").agg(
        reviews=("id", "size"),
        avg_rating=("rating", "mean"),
        problem_share=("sentiment", lambda s: s.isin(PROBLEM_SENTIMENTS).mean() * 100),
    ).round(1).reset_index()


def by_segment(df: pd.DataFrame, top_segments: int = 6) -> pd.DataFrame:
    """Problem share per app version — 'did the latest release make things worse?'"""
    seg = df.dropna(subset=["segment"])
    keep = seg["segment"].value_counts().head(top_segments).index
    seg = seg[seg["segment"].isin(keep)]
    return seg.groupby("segment").agg(
        reviews=("id", "size"),
        problem_share=("sentiment", lambda s: round(s.isin(PROBLEM_SENTIMENTS).mean() * 100, 1)),
        avg_rating=("rating", lambda s: round(s.mean(), 2)),
    ).reset_index().sort_values("reviews", ascending=False)


def baseline_comparison(df: pd.DataFrame, baseline: pd.DataFrame) -> dict:
    """Compare with the old topic model on low-star reviews (BRD §2.2)."""
    merged = df.merge(baseline, left_on="id", right_on="review_id", how="inner")
    low = merged[merged["rating"] <= 3]
    if low.empty:
        return {}
    return {
        "low_star_reviews": int(len(low)),
        "baseline_unclassified": int((low["topic_label_ALL"] == "Undefined").sum()),
        "ai_unclassified": int(low["category"].isin(["Unclassified", "Other"]).sum()),
    }
