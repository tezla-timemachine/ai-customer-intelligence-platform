# AI Customer Intelligence Platform

Turns a CSV of customer reviews into **ranked, evidenced pain points** for a
Product Manager, in minutes instead of days.

Built on **2,618 real Google Play reviews of the Santander UK banking app
(Jan–Sep 2025)**. An existing topic model left **47% of low-star reviews
unclassified**. This platform labels every review and links every insight
back to real customer quotes.

> **Live demo:** [ai-customer-intelligence-version1.streamlit.app](https://ai-customer-intelligence-version1.streamlit.app) · **Case study:** [read it](docs/ai-customer-intelligence-platform-09-product-case-study.md)

![Top pain points from 2,618 Santander reviews](docs/screenshots/dashboard-01-top-pain-points.jpg)

---

## How it works

```
CSV → validate → redact personal data → LLM labels each review (in batches of 20)
    → schema check → code counts, ranks and picks real quotes → dashboard → PM decides
```

**The LLM only reads and labels text.** It assigns a category from a fixed
list, plus sentiment, a short theme and the underlying problem. **Everything
that produces a number, a ranking, a chart or a quote is ordinary code**, so
the counts are exact and repeatable and quotes can't be invented.

The dashboard leads with the answer (the biggest problem), explains every
category and sentiment, and has an **Action summary** that tells Engineering,
Product and Operations what to look at first: example themes, related issues,
app versions, trend and a real quote, downloadable as Markdown for tickets.
[Full architecture and the 17 decisions behind it →](docs/ai-customer-intelligence-platform-03-ai-architecture-and-decision-log.md)

## Run it

```bash
pip install -r requirements.txt
cp .env.example .env          # add your API key, set LLM_PROVIDER
streamlit run app/streamlit_app.py
```

With no key, the app runs in **mock mode**, using keyword rules, not AI. The
whole flow can be tried, and the screen clearly says it isn't AI output.

| Command | What it does |
|---|---|
| `pytest` | Unit tests for validation, redaction, output checking and aggregation |
| `python evals/run_eval.py` | Accuracy against the human-labelled evaluation set |
| `python docs/ai-customer-intelligence-platform-05-make-gantt-chart.py` | Redraws the Gantt chart from the schedule CSV |

### Deploy (Streamlit Community Cloud)

Main file `app/streamlit_app.py`, branch `main`. Paste these into the app's
**Secrets** (never into the repo):

```toml
LLM_PROVIDER = "anthropic"
LLM_MODEL = "claude-haiku-5-5"
ANTHROPIC_API_KEY = "..."
```

The sample analysis ships with the code in `data/precomputed/`, so the demo
loads instantly and costs nothing. New uploads call the AI and are billed to
the key in Secrets, so set a monthly spend limit in the Anthropic Console.

Live since 1 Nov 2026 at https://ai-customer-intelligence-version1.streamlit.app (milestone M6, CR-15).

## Repository

```
app/
  streamlit_app.py        dashboard (upload, pain points, evidence, filters, trends, export)
  pipeline/
    validate.py           step 1 · file and column checks           (code)
    redact.py             step 2 · strip emails, phones, card/account numbers (code)
    classify.py           steps 3–5 · batching, LLM call, schema check, retry (AI + code)
    llm.py                provider switch: anthropic | openai | mock
    aggregate.py          step 6 · counts, ranking, quotes, trends, baseline   (code)
    storage.py            step 7 · SQLite: saved runs, no re-analysis on refresh
    opportunities.py      optional · AI opportunity suggestions, clearly labelled
config/taxonomy.yaml      the 12 categories: edit here, not in code
config/teams.yaml         suggested owner team per category (Action summary page only, not sent to the AI)
prompts/classify_v1.txt   versioned prompt
evals/                    evaluation set, labelling guide, eval script, results
data/                     working dataset (Santander Jan–Sep 2025) + old-model labels
tests/                    pytest
docs/                     brief, BRD, architecture, plan, Gantt, risks, UAT
```

## Documentation

| # | Document |
|---|---|
| 01 | [Product / Business Brief](docs/ai-customer-intelligence-platform-01-product-business-brief.md) |
| 02 | [Business Requirements Document](docs/ai-customer-intelligence-platform-02-business-requirements-document.md) |
| 03 | [AI Architecture & Decision Log](docs/ai-customer-intelligence-platform-03-ai-architecture-and-decision-log.md) |
| 04 | [Project Plan](docs/ai-customer-intelligence-platform-04-project-plan.md) |
| 05 | [Gantt Chart](docs/ai-customer-intelligence-platform-05-gantt-chart.png) |
| 06 | [Risk Register](docs/ai-customer-intelligence-platform-06-risk-register.md) |
| 08 | [User Acceptance Testing](docs/ai-customer-intelligence-platform-08-user-acceptance-testing.xlsx) |
| 09 | [Product Case Study](docs/ai-customer-intelligence-platform-09-product-case-study.md) |
| 10 | [Change Control Log](docs/ai-customer-intelligence-platform-10-change-control-log.md) |
| — | [Changelog](CHANGELOG.md) · [Labelling log](evals/labelling-log.md) · [Handover](HANDOVER.md) |

Document names include the project name and a number for reading order
(renamed from the challenge's suggested `BRD.md` style for clarity).

## Versioning

- **App:** semantic version in `app/__init__.py`, shown in the dashboard sidebar. History in [CHANGELOG.md](CHANGELOG.md).
- **Prompts:** `prompts/classify_vN.txt`. Old versions are kept, and every run and evaluation records which one it used.
- **Taxonomy:** `version` field in `config/taxonomy.yaml`.
- **Documents:** version and change notes in each document's status line.
- **Code:** Git. Each release is tagged (`v0.4.0`).

## Data

[`pcatarino88/banking-app-reviews-data`](https://huggingface.co/datasets/pcatarino88/banking-app-reviews-data)
on Hugging Face has 703,563 public Google Play reviews of six UK banking
apps. Only the small working slice and the evaluation set are included
here. The full file is not republished, because the source states no
licence. It's used for non-commercial portfolio purposes only. See BRD §8.
