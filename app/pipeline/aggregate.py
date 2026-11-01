"""Step 6 — Aggregation (deterministic code). FR-08, FR-09, FR-10, D2, D11.

Everything here is plain pandas: counts, percentages, ranking and quote
selection. No LLM is involved, so the numbers are exact and repeatable.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import yaml

PROBLEM_SENTIMENTS = ("negative", "mixed")
NON_ISSUE = ("Praise", "Unclassified", "Other")  # "Other" is shown separately as a taxonomy-health signal


def _missing(v) -> bool:
    return v is None or (isinstance(v, float) and pd.isna(v)) or str(v).strip().lower() in ("", "none", "nan")


def version_key(v) -> tuple:
    """Sort app versions as numbers, not text: 8.0 < 24.0 < 30.0 < 30.0 (79). (DEF-03)"""
    m = re.match(r"\s*(\d+(?:\.\d+)*)\s*(?:\((\d+)\))?", str(v)) if not _missing(v) else None
    if not m:
        return (1, (), -1, str(v))  # unparseable values sort after real versions
    return (0, tuple(int(x) for x in m.group(1).split(".")), int(m.group(2)) if m.group(2) else -1, "")


def sort_versions(values, newest_first: bool = True) -> list:
    """Distinct app versions in numeric order, for the filter list."""
    return sorted({v for v in values if not _missing(v)}, key=version_key, reverse=newest_first)


def version_label(v) -> str:
    """How a version is shown next to a quote: 'v24.0', or 'version unknown'. (DEF-04)"""
    return "version unknown" if _missing(v) else f"v{v}"


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
    out = seg.groupby("segment").agg(
        reviews=("id", "size"),
        problem_share=("sentiment", lambda s: round(s.isin(PROBLEM_SENTIMENTS).mean() * 100, 1)),
        avg_rating=("rating", lambda s: round(s.mean(), 2)),
    ).reset_index()
    # Busiest versions are kept, but shown in release order, as text labels (DEF-03).
    out = out.iloc[sorted(range(len(out)), key=lambda i: version_key(out["segment"].iloc[i]))].reset_index(drop=True)
    out["segment"] = out["segment"].astype(str)
    return out


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


# --- Plain-English signposting (CR-16) -----------------------------------------
UNCLASSIFIED_MEANING = "The AI could not label this review, for example because the AI service failed. It is never guessed."


def headline(ranked: pd.DataFrame, reviews_in_view: int) -> str:
    """The answer first: the biggest problem in the current selection, in one sentence."""
    if ranked.empty:
        return "No problem reviews in this selection."
    top = ranked.iloc[0]
    n = int(top.negative) + int(top.mixed)
    return (f"**Biggest problem: {top.category}.** It comes up in {n:,} problem reviews "
            f"({int(top.negative):,} negative, {int(top.mixed):,} mixed), "
            f"{top.pct_of_all:g}% of the {reviews_in_view:,} reviews in view.")


def category_glossary(taxonomy: dict) -> pd.DataFrame:
    """What each category means, with a real example, straight from config/taxonomy.yaml."""
    rows = [{"Category": c["name"], "What it covers": c["definition"], "Example review": c["example"]}
            for c in taxonomy["categories"]]
    rows.append({"Category": "Unclassified", "What it covers": UNCLASSIFIED_MEANING, "Example review": ""})
    return pd.DataFrame(rows)


SENTIMENT_NOTES = {
    "negative": "Counts as a full complaint in the pain score.",
    "mixed": "Counts as half a complaint in the pain score.",
    "positive": "Not counted as a problem.",
    "neutral": "Not counted as a problem.",
}


def sentiment_glossary(taxonomy: dict) -> pd.DataFrame:
    """What each sentiment means and how it feeds the ranking."""
    order = ["negative", "mixed", "neutral", "positive"]
    defs = {s["name"]: s["definition"] for s in taxonomy["sentiments"]}
    return pd.DataFrame([{"Sentiment": s, "What it means": defs.get(s, ""), "In the ranking": SENTIMENT_NOTES[s]}
                         for s in order])


# --- Action summary for Engineering, Product and Operations (CR-17) --------------
TEAMS_PATH = Path(__file__).resolve().parents[2] / "config" / "teams.yaml"


def load_teams(path: Path = TEAMS_PATH) -> dict:
    return yaml.safe_load(path.read_text())


def _period_label(months) -> str:
    months = list(months)
    if not months:
        return ""
    a, b = months[0].strftime("%b"), months[-1].strftime("%b %Y")
    return b if len(months) == 1 else f"{a}–{b}"


def _trend(df: pd.DataFrame, sub: pd.DataFrame) -> tuple[str, str]:
    """Is this pain point growing? Compares its share of reviews in the latest months with the months before.

    Uses share of reviews, not raw counts, because review volume itself changes a lot (it jumped 4–5× in July 2025).
    """
    months = sorted(df["date"].dt.to_period("M").unique())
    k = min(3, len(months) // 2)
    if k == 0:
        return "Not enough months", "Needs at least 2 months of reviews in view."
    recent, before = months[-k:], months[-2 * k:-k]
    per_month = df["date"].dt.to_period("M").value_counts()
    sub_month = sub.drop_duplicates("id")["date"].dt.to_period("M")

    def share(ms):
        total = per_month.reindex(ms).fillna(0).sum()
        return sub_month.isin(ms).sum() / total * 100 if total else 0.0

    now, prev = share(recent), share(before)
    n_now, n_prev = int(sub_month.isin(recent).sum()), int(sub_month.isin(before).sum())
    vol_now, vol_prev = per_month.reindex(recent).fillna(0).sum(), per_month.reindex(before).fillna(0).sum()
    if prev == 0 and now == 0:
        label = "Steady"
    elif prev == 0 or now / prev > 1.2:
        label = "Rising ↑"
    elif now / prev < 0.8:
        label = "Falling ↓"
    else:
        label = "Steady"
    detail = (f"{n_now:,} reviews ({now:.1f}% of all) in {_period_label(recent)} vs "
              f"{n_prev:,} ({prev:.1f}%) in {_period_label(before)}")
    volume_jump = bool(vol_prev) and not 0.5 <= vol_now / vol_prev <= 2
    if volume_jump and label != "Steady" and (n_now > n_prev) != label.startswith("Rising"):
        label = "Unclear ↕"  # share and count point different ways because total volume moved a lot
    if volume_jump:
        detail += (f". Total review volume changed {vol_now / vol_prev:.1f}× between these periods, "
                   "so compare with care")
    return label, detail


ACTION_COLUMNS = ["rank", "category", "team", "score", "negative", "mixed", "pct_of_all", "avg_rating",
                  "themes", "raised_with", "versions", "trend", "trend_detail", "quote", "next_step"]


def action_summary(df: pd.DataFrame, teams: dict, top: int = 10) -> pd.DataFrame:
    """One row per ranked pain point: who looks first, what to investigate, where and whether it is growing.

    Everything is counted by code from the labels already made; nothing here calls the AI.
    """
    ranked = pain_points(df, top)
    if ranked.empty:
        return pd.DataFrame(columns=ACTION_COLUMNS)
    m = mentions(df)
    probs = m[m["sentiment"].isin(PROBLEM_SENTIMENTS)]
    owners, default = teams.get("owners", {}), teams.get("default_owner", "Product")
    rows = []
    for rank, r in enumerate(ranked.itertuples(), 1):
        sub = probs[probs["mention"] == r.category]
        # AI themes are short free text, so few repeat: show distinct examples, best evidence first.
        ex = sub.sort_values(["is_main", "confidence"], ascending=False)["theme"].dropna().str.lower()
        themes = list(dict.fromkeys(ex))[:3]
        # Other issues raised in the same reviews: links an outcome (e.g. login) to a cause (e.g. a crash).
        ids = set(sub["id"])
        with_ = probs[probs["id"].isin(ids) & (probs["mention"] != r.category) & ~probs["mention"].isin(NON_ISSUE)]
        raised_with = with_.drop_duplicates(["id", "mention"])["mention"].value_counts().head(3)
        vers = sub.drop_duplicates("id")["segment"]
        vers = vers[~vers.map(_missing)].astype(str).value_counts().head(3)
        trend, detail = _trend(df, sub)
        quote = evidence(df, r.category, n=1)
        team = owners.get(r.category, default)
        rows.append({
            "rank": rank, "category": r.category, "team": team, "score": r.score,
            "negative": int(r.negative), "mixed": int(r.mixed), "pct_of_all": r.pct_of_all, "avg_rating": r.avg_rating,
            "themes": "; ".join(themes),
            "raised_with": ", ".join(f"{c} ({n})" for c, n in raised_with.items()) or "nothing else",
            "versions": ", ".join(f"v{v} ({n})" for v, n in vers.items()) or "not recorded",
            "trend": trend, "trend_detail": detail,
            "quote": quote["feedback"].iloc[0] if not quote.empty else "",
            "next_step": teams.get("teams", {}).get(team, {}).get("next_step", ""),
        })
    return pd.DataFrame(rows, columns=ACTION_COLUMNS)


def action_summary_markdown(actions: pd.DataFrame, title: str) -> str:
    """The action summary as Markdown, grouped by team, ready to paste into a ticket or a Slack message."""
    lines = [f"# {title}", "", "Counted by code from AI-labelled reviews. Suggested owners come from config/teams.yaml "
             "and are a starting point for triage.", ""]
    for team, grp in actions.groupby("team", sort=False):
        lines += [f"## {team}", "", f"Next step: {grp['next_step'].iloc[0]}", ""]
        for a in grp.itertuples():
            lines += [f"### #{a.rank} {a.category}",
                      f"- {a.negative} negative and {a.mixed} mixed reviews ({a.pct_of_all}% of reviews), pain score {a.score:g}",
                      f"- Trend: {a.trend} ({a.trend_detail})",
                      f"- What customers describe (examples): {a.themes}",
                      f"- Often raised together with: {a.raised_with}",
                      f"- App versions most reported: {a.versions}",
                      f"- Example: \"{a.quote.strip()[:300]}\"", ""]
    return "\n".join(lines)
