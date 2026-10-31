"""Unit tests for the deterministic parts of the pipeline (run: pytest)."""
import json
import os

import pandas as pd
import pytest

os.environ["LLM_PROVIDER"] = "mock"

from app.pipeline import aggregate, classify, llm  # noqa: E402
from app.pipeline.redact import redact  # noqa: E402
from app.pipeline.validate import ValidationError, validate  # noqa: E402


# --- validation (FR-01, FR-02) ---------------------------------------------
def csv(text: str) -> bytes:
    return text.strip().encode()


def test_valid_file_accepted():
    df, rep = validate(csv("feedback,date\nGreat app,2025-01-01\nRubbish,2025-01-02"), "x.csv")
    assert len(df) == 2 and rep.rows_accepted == 2


def test_wrong_file_type_rejected():
    with pytest.raises(ValidationError, match=".csv"):
        validate(b"anything", "reviews.xlsx")


def test_missing_column_rejected():
    with pytest.raises(ValidationError, match="date"):
        validate(csv("feedback\nhello"), "x.csv")


def test_empty_rows_and_bad_dates_skipped_and_reported():
    df, rep = validate(csv("feedback,date\nok,2025-01-01\n,2025-01-02\nfine,notadate"), "x.csv")
    assert len(df) == 1
    assert rep.skipped["empty feedback"] == 1 and rep.skipped["unreadable date"] == 1


def test_row_limit():
    body = "feedback,date\n" + "\n".join("x,2025-01-01" for _ in range(5001))
    with pytest.raises(ValidationError, match="limit"):
        validate(body.encode(), "x.csv")


# --- redaction (FR-03) -----------------------------------------------------
@pytest.mark.parametrize("text,token", [
    ("email me at jo.bloggs@gmail.com", "[EMAIL]"),
    ("call 07700 900123 please", "[PHONE]"),
    ("my card 4111 1111 1111 1111 was blocked", "[NUMBER]"),
    ("account 12345678 sort code 09-01-28", "[SORT CODE]"),
])
def test_redaction(text, token):
    out = redact(text)
    assert token in out
    assert not any(ch.isdigit() for ch in out.replace("[", "").replace("]", "")) or token == "[EMAIL]"


def test_redaction_keeps_normal_text():
    assert redact("App update 24.0 broke login") == "App update 24.0 broke login"


# --- structured output check (D3) ------------------------------------------
ALLOWED = {c["name"] for c in classify.load_taxonomy()["categories"]}


def test_invalid_category_and_sentiment_rejected():
    raw = json.dumps([
        {"id": 1, "category": "Login & Access", "sentiment": "negative", "theme": "t", "problem": "p", "confidence": 0.9},
        {"id": 2, "category": "Made Up", "sentiment": "negative", "theme": "t", "problem": "p", "confidence": 0.9},
        {"id": 3, "category": "Praise", "sentiment": "happy", "theme": "t", "problem": None, "confidence": 0.9},
    ])
    labels = classify.parse_and_check(raw, ["1", "2", "3"], ALLOWED)
    assert set(labels) == {"1"}


def test_json_wrapped_in_prose_is_extracted():
    raw = 'Here you go:\n```json\n[{"id": 7, "category": "Praise", "sentiment": "positive", "theme": "easy", "problem": null, "confidence": 0.8}]\n```'
    assert "7" in classify.parse_and_check(raw, ["7"], ALLOWED)


def test_failed_batch_marked_unclassified_never_dropped(monkeypatch):
    monkeypatch.setattr(llm, "complete", lambda prompt: "sorry, I can't do that")
    rows = [(str(i), "text") for i in range(45)]
    labels, stats = classify.classify(rows)
    assert len(labels) == 45
    assert stats.unclassified == 45 and stats.retries == 3
    assert all(v["category"] == classify.UNCLASSIFIED for v in labels.values())


def test_mock_end_to_end_returns_every_id():
    rows = [("1", "Can't log in after update"), ("2", "Great app"), ("3", "Love it but transfers are slow")]
    labels, stats = classify.classify(rows)
    assert set(labels) == {"1", "2", "3"} and stats.unclassified == 0


# --- aggregation (FR-08 – FR-10) -------------------------------------------
@pytest.fixture
def labelled():
    return pd.DataFrame({
        "id": list("abcdefg"),
        "feedback": ["a", "b", "c", "d", "e long quote here", "f", "g"],
        "date": pd.to_datetime(["2025-01-01"] * 7),
        "rating": [1, 1, 2, 3, 1, 5, 5],
        "segment": ["24.0"] * 7,
        "category": ["Login & Access", "Login & Access", "Payments & Transfers", "Payments & Transfers",
                     "Payments & Transfers", "Praise", "Praise"],
        "sentiment": ["negative", "negative", "negative", "mixed", "mixed", "positive", "positive"],
        "theme": ["login fails"] * 2 + ["payee"] * 3 + ["easy"] * 2,
        "confidence": [0.9] * 7,
    })


def test_counts_and_percentages(labelled):
    c = aggregate.by_column(labelled, "category").set_index("category")
    assert c.loc["Payments & Transfers", "count"] == 3
    assert c.loc["Payments & Transfers", "pct"] == round(3 / 7 * 100, 1)


def test_ranking_rule(labelled):
    r = aggregate.pain_points(labelled)
    # Login: 2 negative = 2.0 ; Payments: 1 negative + 2 mixed = 2.0 → tie broken by lower avg rating (Login 1.0)
    assert list(r["category"]) == ["Login & Access", "Payments & Transfers"]
    assert "Praise" not in set(r["category"])


def test_evidence_is_real_rows(labelled):
    ev = aggregate.evidence(labelled, "Payments & Transfers")
    assert set(ev["feedback"]) <= set(labelled["feedback"])


# --- multi-issue reviews (D7 v2) -------------------------------------------
def test_other_categories_filtered_to_valid_distinct_non_main():
    raw = json.dumps([{"id": 1, "category": "Login & Access",
                       "other_categories": ["Performance", "Login & Access", "Made Up", "Performance", "Cards", "Fees & Charges", "Other"],
                       "sentiment": "negative", "theme": "t", "problem": "p", "confidence": 0.9}])
    lab = classify.parse_and_check(raw, ["1"], ALLOWED)["1"]
    assert lab.other_categories == ["Performance", "Cards", "Fees & Charges"]


def test_secondary_issues_count_in_pain_points(labelled):
    df = labelled.assign(other_categories=["Performance", "", "", "", "", "", ""])
    r = aggregate.pain_points(df).set_index("category")
    assert r.loc["Performance", "negative"] == 1 and r.loc["Performance", "as_main_issue"] == 0
    assert r.loc["Login & Access", "as_main_issue"] == 2
    ev = aggregate.evidence(df, "Performance")
    assert list(ev["id"]) == ["a"] and not ev["is_main"].iloc[0]


# --- parallel batches (CR-12) ------------------------------------------------
def _mock_ok(prompt):
    """Valid labels for every review in the prompt, with no network call."""
    return llm._mock(prompt)


def test_parallel_batches_return_every_id_in_order(monkeypatch):
    monkeypatch.setattr(llm, "complete", _mock_ok)
    rows = [(str(i), "Can't log in" if i % 2 else "Great app") for i in range(95)]  # 5 batches
    seen = []
    labels, stats = classify.classify(rows, progress=seen.append)
    assert list(labels) == [str(i) for i in range(95)]  # original order, whatever finished first
    assert stats.batches == 5 and stats.unclassified == 0
    assert seen[-1] == 1.0 and len(seen) == 5


def test_one_failing_batch_does_not_affect_the_others(monkeypatch):
    def flaky(prompt):
        return "not json" if "\n40: " in prompt else _mock_ok(prompt)  # review 40 sits in batch 3
    monkeypatch.setattr(llm, "complete", flaky)
    rows = [(str(i), "Great app") for i in range(60)]
    labels, stats = classify.classify(rows)
    bad = {k for k, v in labels.items() if v["category"] == classify.UNCLASSIFIED}
    assert bad == {str(i) for i in range(40, 60)}  # only batch 3's 20 rows
    assert stats.unclassified == 20 and stats.retries == 1


def test_batches_really_run_at_the_same_time(monkeypatch):
    import threading, time
    live, peak, lock = [0], [0], threading.Lock()
    def slow(prompt):
        with lock:
            live[0] += 1; peak[0] = max(peak[0], live[0])
        time.sleep(0.2)
        with lock:
            live[0] -= 1
        return _mock_ok(prompt)
    monkeypatch.setattr(llm, "complete", slow)
    monkeypatch.setenv("LLM_MAX_CONCURRENCY", "4")
    rows = [(str(i), "Great app") for i in range(160)]  # 8 batches
    t = time.time()
    classify.classify(rows)
    assert peak[0] == 4  # never more than the limit
    assert time.time() - t < 1.2  # 8 × 0.2 s one at a time would take 1.6 s


# --- dashboard fixes (CR-13) ---------------------------------------------------
def test_app_versions_sort_as_numbers_not_text():
    vals = ["8.0", "30.0 (79)", "24.0", "30.0", "16.1", "16.0", None, "nan", "6.0"]
    assert aggregate.sort_versions(vals) == ["30.0 (79)", "30.0", "24.0", "16.1", "16.0", "8.0", "6.0"]


def test_missing_version_is_labelled_not_vnone():
    assert aggregate.version_label(None) == "version unknown"
    assert aggregate.version_label(float("nan")) == "version unknown"
    assert aggregate.version_label("24.0") == "v24.0"


def test_segment_chart_in_release_order():
    df = pd.DataFrame({"id": range(6), "segment": ["24.0", "8.0", "16.1", "24.0", "8.0", "16.1"],
                       "sentiment": ["negative", "positive"] * 3, "rating": [1, 5, 2, 4, 3, 5]})
    assert list(aggregate.by_segment(df)["segment"]) == ["8.0", "16.1", "24.0"]
