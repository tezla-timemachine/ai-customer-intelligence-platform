# Project Handover — AI Customer Intelligence Platform

> **Last updated:** 31 Oct 2026 · **Version:** v0.4.1 · **Repo:** https://github.com/tezla-timemachine/ai-customer-intelligence-platform
>
> Read this first if you're picking the project up in a new session, whether
> you're a person, Claude or Claude Code. It explains what the project is,
> what's done, what's decided and why, and what's next.

---

## 1. What this is

**The product:** a web app that turns a CSV of customer reviews into
**ranked, evidenced pain points** for a Product Manager. An LLM reads each
review and labels it with a category from a fixed list, a sentiment, a short
theme and the underlying problem. **Ordinary code** does all the counting,
ranking, charting and quote selection, so numbers are exact and quotes are
always real.

**Why it exists:** this is **Project 1 of 4** in a 12-week *Applied AI Product
Manager* mentoring programme. The owner, Tez (GitHub `tezla-timemachine`),
is moving into AI Product Management. The mentor's brief ("Weeks 1–2 —
AI Product Management Challenge") has 11 parts. The point the brief keeps
making is being able to explain **why** the product was built this way, not
just that "the coding agent generated it".

| Programme week | Project | Repo (planned name) |
|---|---|---|
| 1–2 | **AI Customer Intelligence Platform** (this repo) | `ai-customer-intelligence-platform` |
| 3–4 | Enterprise Knowledge Copilot (RAG) | `enterprise-knowledge-copilot` |
| 5–7 | AI-Assisted Image Annotation & VLM | `ai-image-annotation-platform` |
| 8–9 | AI Research Agent | `ai-research-agent` |
| 10–12 | Model routing, analytics, experiments, launch | applied across the above |

Plan: one repo per product, all with the same structure, plus a profile
README (`tezla-timemachine/tezla-timemachine`) as the portfolio front page.

---

## 2. Data

- **Source:** [`pcatarino88/banking-app-reviews-data`](https://huggingface.co/datasets/pcatarino88/banking-app-reviews-data),
  703,563 public Google Play reviews of six UK banking apps (Revolut,
  Barclays, Lloyds, Santander, HSBC, Monzo), 2018 – Sep 2025. No licence
  stated, so it's used only for a non-commercial portfolio, and the full
  file is **not** committed.
- **Working dataset:** `data/santander_2025_jan_sep.csv`, Santander, 1 Jan –
  4 Sep 2025, **2,618 reviews**. Columns are mapped to `id, date, feedback,
  rating, segment`, where segment is the app version.
- **Why nine months, not one:** August 2025 alone was unrepresentative.
  Volume jumped 4–5× in July and ratings flipped from mostly 1–2★ to mostly
  5★, probably because the app started asking for ratings in-app. That's an
  open question to investigate.
- **Baseline to beat:** the dataset's own topic-model labels
  (`data/santander_2025_jan_sep_baseline_labels.csv`) leave **436 of 934
  low-star reviews (47%) "Undefined"**.

---

## 3. Status by challenge part

| Part | Deliverable | Status | Where |
|---|---|---|---|
| 1 | Product / Business Brief | ✅ Done | `docs/…-01-product-business-brief.md` |
| 2–3 | MVP scope + BRD (v0.4) | ✅ Done | `docs/…-02-business-requirements-document.md` |
| 4 | AI architecture + decision log (16 decisions) | ✅ Done (D9 updated 31 Oct) | `docs/…-03-…`, diagram `.png` / `.mmd` |
| 5–6 | Project plan + Gantt | ✅ Done (dates need refreshing) | `docs/…-04-project-plan.md`, `…-05-gantt-chart.png`, schedule CSV + script |
| 7 | Risk register (12 risks) | ✅ Done | `docs/…-06-risk-register.md` |
| 8 | Build the MVP | ✅ Built, runs with a real LLM | `app/` |
| 9 | Evaluation set + eval script | ✅ Labelled, **first real run done** | `evals/` |
| 9 | Evaluation results write-up | ✅ Prompt v3 passes the gate (92% / 94%). ⏳ **Next:** write doc 07 | `docs/…-07-ai-evaluation-results.md` (to create) |
| 10 | UAT (26 cases + test files) | ✅ Drafted, ⏳ not yet run | `docs/…-08-user-acceptance-testing.xlsx`, `tests/uat_data/` |
| 11 | Deploy + portfolio + case study | ✅ Case study draft v0.1 written. ⏳ Deploy, screenshots, full-data results | Streamlit Community Cloud; `docs/…-09-product-case-study.md` |

---

## 4. First real evaluation run (31 Oct 2026)

`evals/results/20261031-1318_anthropic-claude-haiku-5-5.md`: model
`claude-haiku-5-5`, prompt `classify_v2`, 50 human-labelled reviews, 0
unclassified, 44 seconds.

| Measure | Result | Target |
|---|---|---|
| Category (main issue) | **80.0%** | ≥ 85% ❌ |
| Sentiment | **94.0%** | ≥ 85% ✅ |
| Category, low-star only | 74.2% | ≥ 85% ❌ |
| AI's main category is one of the human's issues (lenient) | **94.0%** | — |
| Secondary issues: recall / precision | 84.6% / 80.8% | — |
| Duplicates consistent | Yes | — |

### Initial failure analysis

1. **Main-versus-secondary swaps: 7 of the 10 category misses** (E10, E11,
   E14, E24, E36, E44, E47). The AI found the right issues but chose a
   different one as the *main* issue. It's a **definition problem, not a
   comprehension problem**: the lenient score is 94%. The human labels
   aren't fully consistent either. E10 ("transfer button gone, can't send
   money") was labelled by *outcome* (Payments), but E14 ("app keeps
   stopping, can't log in") was labelled by *cause* (Stability).
   → Prompt v3 needs one explicit main-issue rule, and the labels must
   follow the same rule.
2. **Boundary confusions between Stability, Performance, Login and
   Design** (E16, E20, E34). "Loading and connecting problems" → Stability
   or Performance? "Slower to log on" → Login or Performance? "Don't like
   the last update" → Updates or Design? → Sharper definitions with
   boundary examples in the taxonomy.
3. **Negative vs neutral on low-content reviews** (E19, E49, E50).
   Gibberish and "Necessary now all the local branches are closed" were
   labelled neutral. The AI's reading is defensible, and this is the
   only sentiment weakness.

### Prompt v3 run (31 Oct 2026): quality gate passed ✅

Tez chose the **outcome** rule (decision D17). Prompt v3 and taxonomy v3 apply it,
and 6 eval labels were changed to follow it as recorded post-eval changes
(`evals/labelling-log.md`). Result: `evals/results/20261031-1410_anthropic-claude-haiku-5-5.md`.

| Measure | v2, old labels | v2 answers, new labels | **v3, new labels** | Target |
|---|---|---|---|---|
| Category | 80.0% | 84.0% | **92.0%** | ≥ 85% ✅ |
| Category, low-star only | 74.2% | 77.4% | **93.5%** | ≥ 85% ✅ |
| Sentiment | 94.0% | 94.0% | **94.0%** | ≥ 85% ✅ |

The middle column re-scores the v2 answers against the new labels. It separates
the relabel effect (+4 points) from the prompt effect (+8 points). One run, 50
examples, so each review is worth 2 points.

**Remaining misses (v3):** E02 and E18 are new. The outcome rule picked a task
mentioned in passing in a positive or mixed review (Fees, Login) over the main
praise (Design). E20 and E34 are the Stability / Performance / Design boundary
(failure pattern 2, not yet addressed). Sentiment misses are unchanged: E19,
E49, E50 labelled neutral.

**Next:** write `…-07-ai-evaluation-results.md` with the v2 → v3 table, then
the full-data dashboard run.

---

## 5. How it works (short)

```
CSV → validate (code) → redact personal data (code) → batches of 20 → LLM labels
    → schema check, retry once, else "Unclassified" (code) → aggregate, rank, pick real quotes (code)
    → SQLite (saved runs) → Streamlit dashboard → PM decides
```

- **The LLM returns, per review:** `category` (main issue), `other_categories`
  (up to 3), `sentiment` (positive / negative / neutral / mixed), `theme`,
  `problem`, `confidence`.
- **12 categories** in `config/taxonomy.yaml` (v2). Praise is only for
  non-specific praise; specific praise goes to the aspect praised.
- **Ranking rule:** negative mentions + ½ × mixed mentions, counting main
  *and* secondary issues. Praise, Other and Unclassified are excluded.
- **Providers:** `LLM_PROVIDER=anthropic | openai | mock`. Mock uses keyword
  rules and has no AI, for tests only.

Key decisions are in the decision log (D1–D16). The ones to know:
LLM only labels, code counts (D2) · structured JSON + schema check (D3) ·
fixed taxonomy in config (D4/D5) · batches of 20 (D6) · main + up to 3
secondary categories (D7, revised after labelling) · quotes looked up by
row ID, never generated (D11) · old topic-model labels kept out of the
prompt (D16).

---

## 6. Running it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # set LLM_PROVIDER=anthropic, paste ANTHROPIC_API_KEY
pytest                          # 19 tests
python evals/run_eval.py        # accuracy vs evals/eval_set.xlsx → evals/results/
streamlit run app/streamlit_app.py
LOG_PROMPTS=1 streamlit run …   # writes what was sent to the LLM to data/prompt_log.txt
```

**SDK note (31 Oct):** anthropic SDK 2.x removed `temperature`, so it's no
longer sent, and `max_tokens` was raised to 16,000 because the model's
thinking counts towards it. Repeatability (D9) is now checked by the
eval's duplicate-consistency measure rather than enforced by temperature.

---

## 7. Conventions

- **Doc names:** `ai-customer-intelligence-platform-NN-name.ext`, numbered in
  reading order: 07 = evaluation results, 08 = UAT, 09 = case study,
  10 = change control log.
- **Change control:** any change to scope, taxonomy, prompt, model, eval
  labels, data or schedule gets a CR row in doc 10 (raise, assess, Tez
  decides, implement, verify, close). Open proposals: CR-10, CR-11.
- **Versioning:** semantic version in `app/__init__.py` and
  `CHANGELOG.md`. Prompts are `prompts/classify_vN.txt` (old ones kept).
  The taxonomy has a `version`. Each doc has a version in its status line.
  Git tags per release.
- **Secrets:** `.env` is git-ignored. Never commit keys, `data/df_final.parquet`
  or `data/results.db`.
- **Working style Tez prefers:** plain English, one step at a time,
  concrete examples, no jargon dumps. The AI drafts and flags decisions
  that should be Tez's, then Tez pushes back. Tez is UK-based.

---

## 8. Open issues and to-dos

| # | Item | Owner |
|---|---|---|
| 1 | ✅ **Done 31 Oct: commit author fixed.** Both of Tez's commits and the v0.4.0 tag were rewritten to `Terence Field <129769377+tezla-timemachine@users.noreply.github.com>`, keeping the original dates, and force-pushed. The repo's git config now uses that identity. **Still to do (Tez, on github.com):** Settings → Emails → tick "Keep my email addresses private" and "Block command line pushes that expose my email". | Tez |
| 2 | ✅ Outcome rule (D17), prompt v3, re-run done: gate passed. ⏳ Write `…-07-ai-evaluation-results.md` | Together |
| 3 | Run the dashboard on all 2,618 reviews with the real model; sanity-check the pain points | Tez |
| 4 | Run the 26 UAT cases and fill in actual results | Tez |
| 5 | Deploy to Streamlit Community Cloud (API key in app Secrets); add the live link to the README | Together |
| 6 | Case study (`…-09-product-case-study.md`), screenshots, README polish | Together |
| 7 | Refresh the Gantt dates to the real progress | Together |
| 8 | Add a LICENSE (all rights reserved or MIT: Tez to decide) | Tez |
| 9 | Week 2 items not yet built: a list of stored projects (past analyses), and authentication | Later (v0.5) |
| 10 | Open question: what caused the July 2025 volume and rating jump? | Case study |
| 11 | Portfolio front page (`tezla-timemachine/tezla-timemachine` profile README) | Later |

---

## 9. Pushing from a cloud Claude session

The cloud chat session that built v0.4.0 could read this repo but **couldn't
push** (403), even after the Claude GitHub App was installed. Pushes have
been done from **Claude Code on Tez's Mac**, which is logged into GitHub as
`tezla-timemachine`. A new cloud session may work; if it doesn't, use the Mac.
