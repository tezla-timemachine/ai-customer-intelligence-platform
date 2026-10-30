"""Step 8 — Dashboard. Run with:  streamlit run app/streamlit_app.py"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.pipeline import aggregate, llm, opportunities  # noqa: E402
from app.pipeline.classify import PROMPT_VERSION, load_taxonomy  # noqa: E402
from app.pipeline.run import analyse  # noqa: E402
from app.pipeline.validate import ValidationError  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "santander_2025_jan_sep.csv"
BASELINE = ROOT / "data" / "santander_2025_jan_sep_baseline_labels.csv"

st.set_page_config(page_title="AI Customer Intelligence Platform", page_icon="🔎", layout="wide")
st.title("🔎 AI Customer Intelligence Platform")
st.caption("Turns customer reviews into ranked, evidenced pain points. "
           "Categories, sentiment, themes and suggestions are **AI-generated**; counts, rankings and charts are calculated by code.")

if llm.provider() == "mock":
    st.warning("Running in **mock mode** — labels come from simple keyword rules, not AI. "
               "Set `LLM_PROVIDER` and an API key to use a real model.", icon="⚠️")

# --- 1. Upload -------------------------------------------------------------
with st.sidebar:
    st.header("1 · Upload feedback")
    up = st.file_uploader("CSV with columns: feedback, date (+ optional id, rating, segment)", type=None)
    use_sample = st.checkbox("Use sample data (Santander app reviews, Jan–Sep 2025)", value=up is None)
    from app import __version__
    st.caption(f"Model: `{llm.provider()} / {llm.model_name()}` · prompt `{PROMPT_VERSION}` · app v{__version__}")

if up is not None:
    raw, name = up.getvalue(), up.name
elif use_sample and SAMPLE.exists():
    raw, name = SAMPLE.read_bytes(), SAMPLE.name
else:
    st.info("Upload a CSV or tick 'Use sample data' to begin.")
    st.stop()

if st.sidebar.button("Analyse feedback", type="primary") or st.session_state.get("loaded") == name:
    if st.session_state.get("loaded") != name:
        bar = st.progress(0.0, text="Analysing feedback…")
        try:
            df, report, stats, cached = analyse(raw, name, progress=lambda p: bar.progress(p, text=f"Analysing… {p:.0%}"))
        except ValidationError as e:
            bar.empty()
            st.error(f"File rejected: {e}")
            st.stop()
        bar.empty()
        if not cached and stats.get("unclassified", 0) == len(df):
            st.error("The AI service could not label any reviews — check the API key, provider setting and internet "
                     f"connection. First error: {(stats.get('errors') or ['unknown'])[0][:200]}")
            st.stop()
        st.session_state.update(loaded=name, df=df, report=report, stats=stats, cached=cached, opps=None)
else:
    st.info("Press **Analyse feedback** in the sidebar.")
    st.stop()

df: pd.DataFrame = st.session_state.df
report, stats = st.session_state.report, st.session_state.stats
df["date"] = pd.to_datetime(df["date"])

# --- Run summary (FR-15, transparency NFR) ----------------------------------
unclassified = int((df["category"] == "Unclassified").sum())
low_conf = int((df["confidence"] < 0.6).sum())
c1, c2, c3, c4 = st.columns(4)
c1.metric("Reviews analysed", f"{len(df):,}")
c2.metric("Problem reviews (negative/mixed)", f"{df['sentiment'].isin(aggregate.PROBLEM_SENTIMENTS).sum():,}")
c3.metric("Unclassified", f"{unclassified:,}")
c4.metric("Low confidence (<0.6)", f"{low_conf:,}")
st.caption(f"Validation: {report.summary()}" + (" · results loaded from saved run" if st.session_state.cached else
           f" · {stats.get('batches', 0)} batches, {stats.get('retries', 0)} retries, {stats.get('seconds', 0)}s"))

# --- Filters (FR-11) --------------------------------------------------------
with st.sidebar:
    st.header("2 · Filter")
    dmin, dmax = df["date"].min().date(), df["date"].max().date()
    dr = st.date_input("Date range", (dmin, dmax), min_value=dmin, max_value=dmax)
    cats = st.multiselect("Category", sorted(df["category"].dropna().unique()))
    sents = st.multiselect("Sentiment", ["negative", "mixed", "neutral", "positive"])
    segs = st.multiselect("App version", sorted(df["segment"].dropna().unique(), reverse=True))
f = df.copy()
if isinstance(dr, tuple) and len(dr) == 2:
    f = f[(f["date"].dt.date >= dr[0]) & (f["date"].dt.date <= dr[1])]
if cats:  # match the main category OR any secondary category
    f = f[f["category"].isin(cats) | f["other_categories"].fillna("").apply(lambda s: any(c in s.split("; ") for c in cats))]
if sents: f = f[f["sentiment"].isin(sents)]
if segs: f = f[f["segment"].isin(segs)]
if f.empty:
    st.warning("No reviews match these filters."); st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["🎯 Top pain points", "📊 Breakdown", "📈 Trends", "⬇️ Export"])

# --- Top pain points + evidence (FR-09, FR-10) ------------------------------
with tab1:
    ranked = aggregate.pain_points(f)
    if ranked.empty:
        st.info("No negative or mixed reviews in this selection.")
    else:
        st.subheader("Top pain points")
        st.caption("Ranked by code: negative mentions + ½ × mixed mentions, counting every issue a customer raised "
                   "(main or secondary). Click a pain point to see the real customer quotes.")
        other_share = (f["category"] == "Other").mean() * 100
        if other_share > 10:
            st.warning(f"{other_share:.0f}% of reviews fell into 'Other' (target < 10%) — the taxonomy may need a new category.")
        fig = px.bar(ranked.iloc[::-1], x="score", y="category", orientation="h",
                     hover_data=["negative", "mixed", "pct_of_all", "avg_rating"], labels={"score": "Pain score", "category": ""})
        fig.update_layout(height=60 + 38 * len(ranked), margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, width="stretch")
        for i, r in ranked.iterrows():
            with st.expander(f"#{i + 1}  {r.category} — {int(r.negative)} negative, {int(r.mixed)} mixed "
                             f"({r.pct_of_all}% of reviews, main issue in {int(r.as_main_issue)}) · top theme: “{r.top_theme}”"):
                ev = aggregate.evidence(f, r.category, n=5)
                for e in ev.itertuples():
                    stars = "★" * int(e.rating) if pd.notna(e.rating) else ""
                    st.markdown(f"> {e.feedback}\n\n<small>{stars} · {e.date:%d %b %Y} · v{e.segment} · theme: {e.theme}{'' if e.is_main else ' · <i>raised as a secondary issue</i>'}</small>",
                                unsafe_allow_html=True)
        st.divider()
        st.subheader("Opportunity suggestions")
        st.caption("🤖 **AI suggestion** — generated from the ranked pain points and their quotes. For the PM to evaluate, not a decision.")
        if st.button("Suggest opportunities"):
            st.session_state.opps = opportunities.suggest(f, ranked, load_taxonomy()["domain"])
        for o in st.session_state.get("opps") or []:
            st.markdown(f"**{o['pain_point']}** → {o['opportunity']}  \n<small>Why: {o['why']}</small>", unsafe_allow_html=True)

# --- Breakdown (FR-08, FR-12) -----------------------------------------------
with tab2:
    a, b = st.columns(2)
    cat = aggregate.by_column(f, "category")
    a.plotly_chart(px.bar(cat, x="count", y="category", orientation="h", title="Reviews by category",
                          hover_data=["pct"]).update_yaxes(categoryorder="total ascending"), width="stretch")
    sen = aggregate.by_column(f, "sentiment")
    b.plotly_chart(px.pie(sen, names="sentiment", values="count", title="Sentiment split", hole=0.5,
                          color="sentiment", color_discrete_map={"positive": "#16a34a", "negative": "#dc2626",
                                                                 "mixed": "#f59e0b", "neutral": "#94a3b8"}),
                   width="stretch")
    seg = aggregate.by_segment(f)
    if not seg.empty:
        st.plotly_chart(px.bar(seg, x="segment", y="problem_share", hover_data=["reviews", "avg_rating"],
                               title="Share of problem reviews by app version (%)"), width="stretch")
    if BASELINE.exists() and name == SAMPLE.name:
        comp = aggregate.baseline_comparison(f, pd.read_csv(BASELINE, dtype={"review_id": str}))
        if comp:
            st.subheader("Versus the existing topic model (low-star reviews)")
            x, y, z = st.columns(3)
            x.metric("Low-star reviews", f"{comp['low_star_reviews']:,}")
            y.metric("Old model: Undefined", f"{comp['baseline_unclassified']:,}")
            z.metric("This platform: Other/Unclassified", f"{comp['ai_unclassified']:,}")
            st.caption("Coverage only — accuracy is measured separately against the human-labelled evaluation set.")

# --- Trends ------------------------------------------------------------------
with tab3:
    m = aggregate.monthly(f)
    st.plotly_chart(px.bar(m, x="month", y="reviews", title="Reviews per month"), width="stretch")
    st.plotly_chart(px.line(m, x="month", y=["avg_rating", "problem_share"], markers=True,
                            title="Average rating and problem share (%) by month"), width="stretch")

# --- Export (FR-14) -----------------------------------------------------------
with tab4:
    cols = ["id", "date", "rating", "segment", "feedback", "category", "other_categories", "sentiment", "theme", "problem", "confidence"]
    st.dataframe(f[cols], width="stretch", height=400)
    st.download_button("Download labelled reviews (CSV)", f[cols].to_csv(index=False).encode(),
                       file_name="labelled_reviews.csv", mime="text/csv")
