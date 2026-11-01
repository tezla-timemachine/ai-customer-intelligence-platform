"""Step 8 — Dashboard. Run with:  streamlit run app/streamlit_app.py"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.pipeline import aggregate, llm, opportunities, storage  # noqa: E402
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

storage.purge_old_runs()  # delete saved results older than 24 hours on every page load (CR-18)

# --- 1. Upload -------------------------------------------------------------
with st.sidebar:
    st.header("1 · Upload feedback")
    up = st.file_uploader("CSV with columns: feedback, date (+ optional id, rating, segment)", type=None)
    st.caption("🔒 Emails, phone, card and account numbers are removed before reviews go to the AI. "
               "Results are kept for 24 hours so a refresh doesn't re-run the analysis, then deleted.")
    # Untick sample data when a file is uploaded; tick it again when the file is removed (DEF-06).
    st.session_state.setdefault("use_sample", True)
    had_upload = st.session_state.get("_had_upload", False)
    if up is not None and not had_upload:
        st.session_state["use_sample"] = False
    elif up is None and had_upload:
        st.session_state["use_sample"] = True
    st.session_state["_had_upload"] = up is not None
    use_sample = st.checkbox("Use sample data (Santander app reviews, Jan–Sep 2025)", key="use_sample")
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
            # Plain English first; the raw API message is there for whoever fixes it (DEF-06).
            st.error("The AI service couldn't label any reviews, so nothing was saved. Check the API key, the "
                     "provider setting and your internet connection, then press **Analyse feedback** again.")
            with st.expander("Technical details"):
                st.code((stats.get("errors") or ["unknown"])[0][:500])
            st.stop()
        st.session_state.update(loaded=name, df=df, report=report, stats=stats, cached=cached, opps=None)
else:
    st.info("Press **Analyse feedback** in the sidebar.")
    st.stop()

df: pd.DataFrame = st.session_state.df
report, stats = st.session_state.report, st.session_state.stats
df["date"] = pd.to_datetime(df["date"])

# --- Filters (FR-11) --------------------------------------------------------
with st.sidebar:
    st.header("2 · Filter")
    dmin, dmax = df["date"].min().date(), df["date"].max().date()
    dr = st.date_input("Date range", (dmin, dmax), min_value=dmin, max_value=dmax)
    st.caption("Pick a start and an end date, then click outside the box to apply.")  # DEF-05
    cats = st.multiselect("Category", sorted(df["category"].dropna().unique()),
                          help="The topic of a customer's issue, e.g. Cards or Login & Access. Matches a review's main "
                               "issue or any other issue it raises. Definitions: 'What do the categories and sentiments "
                               "mean?' at the top of the page.")
    sents = st.multiselect("Sentiment", ["negative", "mixed", "neutral", "positive"],
                           help="**negative**: only complaints · **mixed**: praise and a complaint · **neutral**: "
                                "factual, no clear feeling · **positive**: only praise. Negative and mixed reviews "
                                "count as problem reviews.")
    segs = st.multiselect("App version", aggregate.sort_versions(df["segment"]))  # numeric order, newest first (DEF-03)
f = df.copy()
if isinstance(dr, tuple) and len(dr) == 2:
    f = f[(f["date"].dt.date >= dr[0]) & (f["date"].dt.date <= dr[1])]
if cats:  # match the main category OR any secondary category
    f = f[f["category"].isin(cats) | f["other_categories"].fillna("").apply(lambda s: any(c in s.split("; ") for c in cats))]
if sents: f = f[f["sentiment"].isin(sents)]
if segs: f = f[f["segment"].isin(segs)]
filtered = len(f) < len(df)

# --- Answer first and signposting (CR-16) -------------------------------------
ranked = aggregate.pain_points(f) if not f.empty else pd.DataFrame()
if not f.empty:
    st.success(aggregate.headline(ranked, len(f)) +
               ("  \nOpen it under **Top pain points** below to read what customers actually said." if not ranked.empty else ""),
               icon="🎯")
st.markdown("**How to read this page:** ① **Top pain points** ranks customer problems, worst first. "
            "② Click a pain point to read real customer quotes. "
            "③ Use the filters in the left-hand menu (tap **»** at the top left on a phone) to narrow by date, "
            "category, sentiment or app version.")
with st.expander("📖 What do the categories and sentiments mean?"):
    taxonomy = load_taxonomy()
    st.markdown("**Categories:** what a review is about. Each review gets one main category, plus up to 3 others "
                "if it raises several issues.")
    st.table(aggregate.category_glossary(taxonomy).set_index("Category"))  # st.table wraps long text
    st.markdown("**Sentiments:** how the customer feels. Negative and mixed reviews count as **problem reviews**.")
    st.table(aggregate.sentiment_glossary(taxonomy).set_index("Sentiment"))

# --- Run summary (FR-15, transparency NFR): follows the filters (DEF-01) ------
unclassified = int((f["category"] == "Unclassified").sum())
low_conf = int((f["confidence"] < 0.6).sum())
c1, c2 = st.columns(2)
c1.metric("Reviews in view" if filtered else "Reviews analysed", f"{len(f):,}",
          help="Customer reviews included in everything on this page.")
c2.metric("Problem reviews", f"{f['sentiment'].isin(aggregate.PROBLEM_SENTIMENTS).sum():,}",
          help="Reviews where the customer complains: negative, or mixed (praise and a complaint).")
# Data quality stays visible (transparency NFR), but small, with its meaning spelled out.
low_pct = f" ({low_conf / len(f):.0%})" if len(f) else ""
st.caption(f"**Data quality:** {unclassified:,} unclassified (the AI couldn't label them) · "
           f"{low_conf:,} low-confidence labels{low_pct}, where the AI was less than 60% sure. "
           "Low-confidence labels are still counted; read their quotes before relying on a small category.")
if filtered:
    st.caption(f"🔎 Filters on: showing **{len(f):,} of {len(df):,}** reviews in the file. Every number, chart, quote and export below uses this selection.")
st.caption(f"Validation: {report.summary()}" + (" · results loaded from saved run" if st.session_state.cached else
           f" · {stats.get('batches', 0)} batches, {stats.get('retries', 0)} retries, {stats.get('seconds', 0)}s"))
if f.empty:
    st.warning("No reviews match these filters."); st.stop()

tab1, tab_act, tab2, tab3, tab4 = st.tabs(["🎯 Top pain points", "🛠️ Action summary", "📊 Breakdown", "📈 Trends", "⬇️ Export"])

# --- Top pain points + evidence (FR-09, FR-10) ------------------------------
with tab1:
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
                     custom_data=["negative", "mixed", "pct_of_all", "avg_rating"], labels={"score": "Pain score", "category": ""})
        fig.update_traces(hovertemplate="<b>%{y}</b><br>%{customdata[0]} negative and %{customdata[1]} mixed reviews"
                                        "<br>In %{customdata[2]}% of all reviews in view"
                                        "<br>Average star rating: %{customdata[3]:.1f} out of 5"
                                        "<br>Pain score: %{x} (negative + half of mixed)<extra></extra>")
        fig.update_layout(height=60 + 38 * len(ranked), margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, width="stretch")
        for i, r in ranked.iterrows():
            with st.expander(f"#{i + 1}  {r.category} — {int(r.negative)} negative, {int(r.mixed)} mixed "
                             f"({r.pct_of_all}% of reviews, main issue in {int(r.as_main_issue)}) · top theme: “{r.top_theme}”"):
                ev = aggregate.evidence(f, r.category, n=5)
                for e in ev.itertuples():
                    stars = "★" * int(e.rating) if pd.notna(e.rating) else ""
                    st.markdown(f"> {e.feedback}\n\n<small>{stars} · {e.date:%d %b %Y} · {aggregate.version_label(e.segment)} · theme: {e.theme}{'' if e.is_main else ' · <i>raised as a secondary issue</i>'}</small>",
                                unsafe_allow_html=True)
        st.divider()
        st.subheader("Opportunity suggestions")
        st.caption("🤖 **AI suggestion** — generated from the ranked pain points and their quotes. For the PM to evaluate, not a decision.")
        if st.button("Suggest opportunities"):
            st.session_state.opps = opportunities.suggest(f, ranked, load_taxonomy()["domain"])
        for o in st.session_state.get("opps") or []:
            st.markdown(f"**{o['pain_point']}** → {o['opportunity']}  \n<small>Why: {o['why']}</small>", unsafe_allow_html=True)

# --- Action summary for Engineering / Product / Operations (CR-17) -----------
with tab_act:
    st.subheader("Action summary")
    st.caption("What each team should look at first. Counted by code from the labelled reviews, with no extra AI calls. "
               "Suggested owners come from `config/teams.yaml` and are a starting point for triage, not a decision. "
               "Follows the filters on the left.")
    actions = aggregate.action_summary(f, aggregate.load_teams())
    if actions.empty:
        st.info("No problem reviews in this selection, so there is nothing to action.")
    else:
        team_counts = actions["team"].value_counts()
        pick = st.radio("Show actions for", ["All teams"] + list(team_counts.index), horizontal=True,
                        format_func=lambda t: t if t == "All teams" else f"{t} ({team_counts[t]})")
        view = actions if pick == "All teams" else actions[actions["team"] == pick]
        for team, grp in view.groupby("team", sort=False):
            st.markdown(f"#### {team}")
            st.caption(f"Suggested next step: {grp['next_step'].iloc[0]}")
            for a in grp.itertuples():
                with st.container(border=True):
                    st.markdown(f"**#{a.rank} {a.category}** · {a.negative} negative, {a.mixed} mixed "
                                f"({a.pct_of_all}% of reviews) · **{a.trend}**")
                    st.markdown(f"- **What customers describe (examples):** {a.themes or 'no themes recorded'}\n"
                                f"- **Often raised together with:** {a.raised_with}\n"
                                f"- **App versions most reported:** {a.versions}\n"
                                f"- **Trend:** {a.trend_detail}")
                    if a.quote:
                        st.markdown(f"> {a.quote.strip()[:300]}")
        title = f"Action summary: {name}" + (" (filtered)" if filtered else "")
        st.download_button("Download action summary (Markdown, for tickets or Slack)",
                           aggregate.action_summary_markdown(view, title).encode(),
                           file_name="action_summary.md", mime="text/markdown")

# --- Breakdown (FR-08, FR-12) -----------------------------------------------
with tab2:
    a, b = st.columns(2)
    cat = aggregate.by_column(f, "category")
    a.plotly_chart(px.bar(cat, x="count", y="category", orientation="h", title="Reviews by category (main issue)",
                          hover_data=["pct"], labels={"count": "Reviews", "category": "", "pct": "% of reviews"})
                   .update_yaxes(categoryorder="total ascending"), width="stretch")
    sen = aggregate.by_column(f, "sentiment")
    b.plotly_chart(px.pie(sen, names="sentiment", values="count", title="Sentiment split", hole=0.5,
                          color="sentiment", color_discrete_map={"positive": "#16a34a", "negative": "#dc2626",
                                                                 "mixed": "#f59e0b", "neutral": "#94a3b8"}),
                   width="stretch")
    seg = aggregate.by_segment(f)
    if not seg.empty:
        # Versions as labels in release order, not as numbers on a scale (DEF-03).
        st.plotly_chart(px.bar(seg, x="segment", y="problem_share", hover_data=["reviews", "avg_rating"],
                               title="Share of problem reviews by app version (busiest 6 versions)",
                               labels={"segment": "App version", "problem_share": "Problem reviews (%)",
                                       "reviews": "Reviews", "avg_rating": "Average rating"},
                               category_orders={"segment": list(seg["segment"])})
                        .update_xaxes(type="category").update_yaxes(range=[0, 100]), width="stretch")
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
    st.plotly_chart(px.bar(m, x="month", y="reviews", title="Reviews per month",
                           labels={"month": "Month", "reviews": "Reviews"}), width="stretch")
    # Rating (1–5) and problem share (0–100%) get their own charts and scales (DEF-02).
    r1, r2 = st.columns(2)
    r1.plotly_chart(px.line(m, x="month", y="avg_rating", markers=True, title="Average star rating by month",
                            labels={"month": "Month", "avg_rating": "Average rating (1–5)"})
                    .update_yaxes(range=[1, 5]), width="stretch")
    r2.plotly_chart(px.line(m, x="month", y="problem_share", markers=True, title="Problem reviews by month (%)",
                            labels={"month": "Month", "problem_share": "Negative or mixed (%)"},
                            color_discrete_sequence=["#dc2626"])
                    .update_yaxes(range=[0, 100]), width="stretch")

# --- Export (FR-14) -----------------------------------------------------------
with tab4:
    cols = ["id", "date", "rating", "segment", "feedback", "category", "other_categories", "sentiment", "theme", "problem", "confidence"]
    st.dataframe(f[cols], width="stretch", height=400)
    st.download_button("Download labelled reviews (CSV)", f[cols].to_csv(index=False).encode(),
                       file_name="labelled_reviews.csv", mime="text/csv")
