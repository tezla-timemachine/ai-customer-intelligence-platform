"""Step 7 — Storage (SQLite). Saved results mean a refresh never re-runs or re-pays (D14).

Saved runs hold the original review text, so they are deleted after 24 hours (privacy NFR, CR-18).
The shipped sample is not lost: it reloads from data/precomputed/ at no cost.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "results.db"
# Finished results shipped with the code (CR-14), named by file hash. Used when the database has no
# saved run, e.g. on a fresh cloud deployment, so the sample loads instantly and costs nothing.
PRECOMPUTED_DIR = Path(__file__).resolve().parents[2] / "data" / "precomputed"
KEEP_HOURS = 24  # BRD privacy NFR: uploads are deleted after the session / 24 hours (CR-18)


def _conn(path: Path = DB_PATH) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute("PRAGMA secure_delete = ON")  # overwrite deleted text on disk instead of leaving it in free space
    con.execute("""CREATE TABLE IF NOT EXISTS runs (
        run_id TEXT PRIMARY KEY, file_hash TEXT, filename TEXT, created_at TEXT,
        provider TEXT, model TEXT, prompt_version TEXT, rows INTEGER, stats_json TEXT)""")
    return con


def file_hash(raw: bytes, provider: str, model: str, prompt_version: str) -> str:
    """Same file + same model + same prompt = same results, so we can reuse them."""
    h = hashlib.sha256(raw)
    h.update(f"{provider}|{model}|{prompt_version}".encode())
    return h.hexdigest()[:16]


def purge_old_runs(path: Path = DB_PATH, hours: float = KEEP_HOURS, now: datetime | None = None) -> int:
    """Delete saved runs older than `hours`, with their results. Returns how many were deleted."""
    cutoff = (now or datetime.now(timezone.utc)) - timedelta(hours=hours)
    with _conn(path) as con:
        old = [run_id for run_id, created in con.execute("SELECT run_id, created_at FROM runs")
               if datetime.fromisoformat(created) < cutoff]
        for run_id in old:
            con.execute(f'DROP TABLE IF EXISTS "labels_{run_id}"')
            con.execute("DELETE FROM runs WHERE run_id=?", (run_id,))
    return len(old)


def find_run(fhash: str, path: Path = DB_PATH, precomputed_dir: Path = PRECOMPUTED_DIR) -> pd.DataFrame | None:
    purge_old_runs(path)  # every analysis checks here first, so expired uploads never come back
    with _conn(path) as con:
        row = con.execute("SELECT run_id FROM runs WHERE file_hash=? ORDER BY created_at DESC LIMIT 1", (fhash,)).fetchone()
        if row:
            return pd.read_sql(f'SELECT * FROM "labels_{row[0]}"', con, parse_dates=["date"])
    # No saved run: fall back to shipped results for exactly this file + model + prompt (CR-14).
    shipped = precomputed_dir / f"{fhash}.csv"
    if shipped.exists():
        df = pd.read_csv(shipped, dtype={"id": str, "segment": str, "other_categories": str}, parse_dates=["date"])
        df["other_categories"] = df["other_categories"].fillna("")  # CSV turns "" into NaN; keep it as saved
        save_run(df, fhash, shipped.name, {"source": "precomputed"}, path)
        return df
    return None


def export_run(fhash: str, path: Path = DB_PATH, precomputed_dir: Path = PRECOMPUTED_DIR) -> Path:
    """Write the latest saved run for this hash to data/precomputed/, ready to ship."""
    with _conn(path) as con:
        row = con.execute("SELECT run_id FROM runs WHERE file_hash=? ORDER BY created_at DESC LIMIT 1", (fhash,)).fetchone()
        if not row:
            raise LookupError("No saved run for this file, model and prompt.")
        df = pd.read_sql(f'SELECT * FROM "labels_{row[0]}"', con)
    precomputed_dir.mkdir(parents=True, exist_ok=True)
    out = precomputed_dir / f"{fhash}.csv"
    df.to_csv(out, index=False)
    return out


def save_run(df: pd.DataFrame, fhash: str, filename: str, stats: dict, path: Path = DB_PATH) -> str:
    run_id = f"{datetime.now(timezone.utc):%Y%m%d%H%M%S}_{fhash[:6]}"
    with _conn(path) as con:
        df.to_sql(f"labels_{run_id}", con, index=False)
        con.execute("INSERT INTO runs VALUES (?,?,?,?,?,?,?,?,?)", (
            run_id, fhash, filename, datetime.now(timezone.utc).isoformat(),
            stats.get("provider"), stats.get("model"), stats.get("prompt_version"), len(df), json.dumps(stats)))
    return run_id
