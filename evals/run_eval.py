"""Part 9 — Compare Expected Output vs AI Output on the human-labelled evaluation set.

Usage:
    python evals/run_eval.py                       # uses evals/eval_set.xlsx (or .csv)
    LLM_PROVIDER=anthropic python evals/run_eval.py

Writes:
    evals/results/<timestamp>_<model>.csv   one row per example, expected vs AI
    evals/results/<timestamp>_<model>.md    summary: accuracy, by case type, failure patterns
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.pipeline import classify, llm  # noqa: E402
from app.pipeline.redact import redact  # noqa: E402

EVAL_DIR = ROOT / "evals"
OUT_DIR = EVAL_DIR / "results"
TARGET = 85.0


def load_eval_set() -> pd.DataFrame:
    xlsx, csv = EVAL_DIR / "eval_set.xlsx", EVAL_DIR / "eval_set.csv"
    df = pd.read_excel(xlsx, sheet_name="eval_set") if xlsx.exists() else pd.read_csv(csv)
    df = df.fillna("").astype({"expected_category": str, "expected_sentiment": str})
    # Labels can be typed as numbers/letters (see the 'categories' sheet) or full names.
    cats = [c["name"] for c in classify.load_taxonomy()["categories"]]
    cat_codes = {str(i): c for i, c in enumerate(cats, 1)} | {c.lower(): c for c in cats}
    sent_codes = {"p": "positive", "n": "negative", "u": "neutral", "m": "mixed",
                  "positive": "positive", "negative": "negative", "neutral": "neutral", "mixed": "mixed"}
    def norm(v, codes):
        v = v.strip().removesuffix(".0").lower()
        return codes.get(v, v if v == "" else f"?{v}")
    df["expected_category"] = df["expected_category"].map(lambda v: norm(v, cat_codes))
    df["expected_sentiment"] = df["expected_sentiment"].map(lambda v: norm(v, sent_codes))
    # Optional secondary categories: comma/semicolon separated numbers or names, e.g. "4, 1"
    if "expected_other_categories" not in df.columns:
        df["expected_other_categories"] = ""
    def norm_list(v):
        parts = [x for x in str(v).replace(";", ",").split(",") if x.strip()]
        return "; ".join(norm(x, cat_codes) for x in parts)
    df["expected_other_categories"] = df["expected_other_categories"].map(norm_list)
    bad = df[df["expected_category"].str.startswith("?") | df["expected_sentiment"].str.startswith("?")
             | df["expected_other_categories"].str.contains(r"\?", regex=True)]
    if len(bad):
        sys.exit("Unrecognised labels in: " + ", ".join(bad["eval_id"]) + ". Use the numbers/letters in the 'categories' sheet.")
    unlabelled = df[(df["expected_category"] == "") | (df["expected_sentiment"] == "")]
    if len(unlabelled):
        sys.exit(f"{len(unlabelled)} examples have no expected label yet ({', '.join(unlabelled['eval_id'][:5])}…). "
                 "Label them first — see evals/labelling-guide.md.")
    return df


def pct(x: pd.Series) -> float:
    return round(x.mean() * 100, 1) if len(x) else float("nan")


def main() -> None:
    if llm.provider() == "mock":
        print("WARNING: LLM_PROVIDER=mock — these results measure keyword rules, not AI. Do not report them.\n")
    ev = load_eval_set()
    rows = [(r.eval_id, redact(str(r.feedback))) for r in ev.itertuples()]
    labels, stats = classify.classify(rows)
    ai = pd.DataFrame(labels.values()).rename(columns={"id": "eval_id", "category": "ai_category",
                                                       "sentiment": "ai_sentiment", "theme": "ai_theme",
                                                       "problem": "ai_problem", "confidence": "ai_confidence",
                                                       "other_categories": "ai_other_categories"})
    res = ev.merge(ai, on="eval_id", how="left")
    res["category_ok"] = res["expected_category"].str.strip() == res["ai_category"]
    res["sentiment_ok"] = res["expected_sentiment"].str.strip().str.lower() == res["ai_sentiment"]
    res["both_ok"] = res["category_ok"] & res["sentiment_ok"]

    # Multi-issue scoring: compare the full SET of issues, not just the main one.
    split = lambda s: {x.strip() for x in str(s).split(";") if x.strip()}
    exp_all = res.apply(lambda r: {r.expected_category} | split(r.expected_other_categories), axis=1)
    ai_all = res.apply(lambda r: {r.ai_category} | split(r.ai_other_categories), axis=1)
    res["main_issue_found"] = [a in e for a, e in zip(res["ai_category"], exp_all)]  # AI main is one of your issues
    exp_sec = res["expected_other_categories"].map(split)
    ai_sec = res["ai_other_categories"].map(split)
    sec_expected = sum(len(s) for s in exp_sec)
    sec_found = sum(len(e & a) for e, a in zip(exp_sec, ai_all))
    sec_flagged = sum(len(s) for s in ai_sec)
    sec_correct = sum(len(a & e) for a, e in zip(ai_sec, exp_all))
    sec_recall = round(sec_found / sec_expected * 100, 1) if sec_expected else float("nan")
    sec_precision = round(sec_correct / sec_flagged * 100, 1) if sec_flagged else float("nan")

    cat_acc, sen_acc = pct(res["category_ok"]), pct(res["sentiment_ok"])
    low = res[res["rating"].astype(int) <= 3]
    by_case = res.groupby("case_type").agg(n=("eval_id", "size"), category=("category_ok", pct),
                                           sentiment=("sentiment_ok", pct)).reset_index()
    wrong = res[~res["category_ok"]]
    confusions = (wrong.groupby(["expected_category", "ai_category"]).size()
                  .sort_values(ascending=False).rename("count").reset_index())
    sent_conf = (res[~res["sentiment_ok"]].groupby(["expected_sentiment", "ai_sentiment"]).size()
                 .sort_values(ascending=False).rename("count").reset_index())
    dups = res[res["case_type"] == "duplicate"]
    dup_consistent = dups[["ai_category", "ai_sentiment"]].drop_duplicates().shape[0] <= 1 if len(dups) else True

    OUT_DIR.mkdir(exist_ok=True)
    stamp = f"{datetime.now():%Y%m%d-%H%M}_{llm.provider()}-{llm.model_name()}".replace("/", "-")
    res.to_csv(OUT_DIR / f"{stamp}.csv", index=False)

    gate = "PASS ✅" if cat_acc >= TARGET and sen_acc >= TARGET else "FAIL ❌"
    md = [f"# Evaluation run — {stamp}", "",
          f"- Model: `{stats.provider} / {stats.model}` · prompt `{stats.prompt_version}`",
          f"- Examples: {len(res)} · unclassified: {stats.unclassified} · retries: {stats.retries} · time: {stats.seconds}s",
          f"- **Quality gate (≥{TARGET:.0f}% category and sentiment): {gate}**", "",
          "| Measure | Accuracy |", "|---|---|",
          f"| Category | {cat_acc}% |", f"| Sentiment | {sen_acc}% |", f"| Both correct | {pct(res['both_ok'])}% |",
          f"| Category — low-star reviews only (n={len(low)}) | {pct(low['category_ok'])}% |",
          f"| Sentiment — low-star reviews only | {pct(low['sentiment_ok'])}% |",
          f"| Duplicates labelled consistently | {'Yes' if dup_consistent else 'No'} |",
          f"| AI main category is one of the issues you listed (lenient) | {pct(res['main_issue_found'])}% |",
          f"| Secondary issues found (recall, n={sec_expected}) | {sec_recall}% |",
          f"| Secondary issues flagged that were right (precision, n={sec_flagged}) | {sec_precision}% |", "",
          "## By case type", "", by_case.to_markdown(index=False), "",
          "## Most common category confusions (expected → AI)", "",
          confusions.head(10).to_markdown(index=False) if len(confusions) else "None", "",
          "## Sentiment confusions (expected → AI)", "",
          sent_conf.to_markdown(index=False) if len(sent_conf) else "None", "",
          "## Every failure", ""]
    for r in res[~res["both_ok"]].itertuples():
        md.append(f"- **{r.eval_id}** ({r.case_type}, {r.rating}★) “{str(r.feedback)[:160]}” — expected "
                  f"*{r.expected_category} / {r.expected_sentiment}*" + (f" (+ {r.expected_other_categories})" if r.expected_other_categories else "")
                  + f", AI *{r.ai_category} / {r.ai_sentiment}*" + (f" (+ {r.ai_other_categories})" if r.ai_other_categories else ""))
    md += ["", "## Failure patterns (fill in after reading the failures)", "", "1. ", "2. ", "3. "]
    (OUT_DIR / f"{stamp}.md").write_text("\n".join(md))
    print("\n".join(md[:17]))
    print(f"\nFull results: {OUT_DIR / (stamp + '.md')}")


if __name__ == "__main__":
    main()
