"""Step 1 — Input validation (deterministic code). FR-01, FR-02."""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

REQUIRED = ["feedback", "date"]
OPTIONAL = ["id", "rating", "segment"]
MAX_ROWS = 5000
MAX_BYTES = 5 * 1024 * 1024


class ValidationError(Exception):
    """Raised when a file cannot be analysed at all."""


@dataclass
class ValidationReport:
    rows_received: int = 0
    rows_accepted: int = 0
    skipped: dict[str, int] = field(default_factory=dict)

    def summary(self) -> str:
        parts = [f"{self.rows_accepted:,} of {self.rows_received:,} rows accepted"]
        parts += [f"{n:,} skipped: {why}" for why, n in self.skipped.items() if n]
        return " · ".join(parts)


def validate(raw: bytes, filename: str) -> tuple[pd.DataFrame, ValidationReport]:
    """Return a clean DataFrame (id, feedback, date, rating, segment) and a report."""
    if not filename.lower().endswith(".csv"):
        raise ValidationError("Please upload a .csv file.")
    if len(raw) > MAX_BYTES:
        raise ValidationError(f"File is larger than {MAX_BYTES // (1024 * 1024)} MB.")
    try:
        from io import BytesIO
        df = pd.read_csv(BytesIO(raw))
    except Exception as exc:  # malformed CSV
        raise ValidationError(f"Could not read the file as CSV ({exc}).") from exc

    df.columns = [c.strip().lower() for c in df.columns]
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValidationError(f"Missing required column(s): {', '.join(missing)}.")
    if len(df) > MAX_ROWS:
        raise ValidationError(f"File has {len(df):,} rows; the limit is {MAX_ROWS:,}.")

    report = ValidationReport(rows_received=len(df))
    if "id" not in df.columns:
        df["id"] = range(1, len(df) + 1)
    for col in ["rating", "segment"]:
        if col not in df.columns:
            df[col] = None

    df["feedback"] = df["feedback"].astype("string").str.strip()
    empty = df["feedback"].isna() | (df["feedback"] == "")
    report.skipped["empty feedback"] = int(empty.sum())
    df = df[~empty]

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    bad_date = df["date"].isna()
    report.skipped["unreadable date"] = int(bad_date.sum())
    df = df[~bad_date]

    dup_id = df["id"].duplicated()
    report.skipped["duplicate id"] = int(dup_id.sum())
    df = df[~dup_id]

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["segment"] = df["segment"].astype("string")
    report.rows_accepted = len(df)
    if report.rows_accepted == 0:
        raise ValidationError("No usable rows after validation.")
    return df[["id", "feedback", "date", "rating", "segment"]].reset_index(drop=True), report
