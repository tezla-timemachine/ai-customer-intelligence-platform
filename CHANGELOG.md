# Changelog

All notable changes to the AI Customer Intelligence Platform.
Format based on [Keep a Changelog](https://keepachangelog.com/). Versions follow
[semantic versioning](https://semver.org/): MAJOR.MINOR.PATCH.

Document versions (e.g. BRD v0.4) are tracked in each document's status line.
Prompt versions live in `prompts/` and are recorded against every analysis run
and evaluation result.

## [Unreleased]
### Changed
- **Prompt v3 and taxonomy v3:** the main issue is now chosen by *outcome*, the task the customer was trying to do that went wrong. The cause becomes a secondary issue (decision D17). Prompt v2 is kept for comparison.
- **Evaluation set:** 6 main-category labels changed to follow the outcome rule (E13, E14, E24, E41, E44, E47). They are recorded as post-eval changes in `evals/labelling-log.md` and in each row's label notes.
- Labelling guide updated to the outcome rule.
### Added
- Decision D17 and a dated decision history (§3.1) in the architecture and decision log.
- Product case study, draft v0.1 (doc 09): problem, user, AI opportunity, decisions, architecture, MVP, evaluation, what failed, what changed, results and next iteration.
- Change control log (doc 10): every change to scope, taxonomy, prompt, model, labels, data or schedule gets a change record (CR-01 to CR-11, back-filled from 30 Oct).
- Eval run with prompt v3: **category 92.0%, sentiment 94.0%. The quality gate passes (milestone M4).** Low-star category accuracy rose from 74.2% to 93.5%.
- Full-data run on all 2,618 reviews (prompt v3): every review labelled, 1.9% "Other", **$0.26 for the run (about $0.10 per 1,000 reviews)**, about 30 minutes. Speed misses the 8-minute target (CR-12 proposed).
- Dashboard screenshots in `docs/screenshots/`, used in the case study (now draft v0.2) and the README.
- UAT run (26 cases): **22 pass, 3 fail, 1 not run. All 12 AI cases pass.** Fails: full-run speed (UAT-06), summary numbers ignore filters (UAT-09), unreadable rating chart (UAT-12). Results, and a new Defects sheet, are in the UAT workbook. Fixes proposed as CR-13.
- **Speed fix (CR-12):** LLM batches are sent in parallel (5 at once), `max_tokens` lowered to 12,000 and SDK retries raised to 6, all tunable in `.env`. Full run 30 min → 6.1 min; eval 38 s → 18.6 s; cost and accuracy unchanged. UAT-06 re-tested and now passes (UAT: 23 pass, 2 fail, 1 not run). 3 new tests (22 in total).
- **Dashboard fixes (CR-13):** summary numbers follow the filters and say "showing X of Y"; rating and problem share have separate charts; app versions are sorted by number and plotted as labels; "version unknown" replaces "vNone"; a hint explains the date range; "Use sample data" re-ticks when an upload is removed; the AI-unavailable error is in plain English, with technical details in an expander. 3 new tests (25 in total). UAT-09 and UAT-12 re-tested and pass: **UAT 25 pass, 0 fail, 1 not run.**
- New screenshot: rating and problem share by month.
- **Deployment readiness (CR-14):** the finished sample analysis ships in `data/precomputed/` and loads in about 1 second with no AI cost when there's no saved run, as on a fresh cloud deployment. `requirements.txt` is pinned to the tested versions. README has a deploy section. 1 new test (26 in total).
- **Plain-English signposting (CR-16):** first-look feedback on the live app said the dashboard was hard to read. It now leads with the answer ("Biggest problem: …") and a three-step "How to read this page" guide; a "What do the categories and sentiments mean?" panel shows every definition with an example; the chart's hover box is in plain English instead of raw field names; the headline numbers have "?" tooltips; and the unclassified and low-confidence counts move to a smaller "Data quality" line that explains them. Filters have tooltips, including the sentiment definitions. Fixes DEF-07 to DEF-10. 2 new tests.
- **Action summary page (CR-17):** a new tab that tells Engineering, Product and Operations what to look at first. For each ranked pain point: suggested owner team (from the new `config/teams.yaml`), example themes, the issues customers raise with it, the app versions most reported, a trend that warns when review volume changed a lot, a real quote and a suggested next step. Filter by team; download as Markdown for tickets or Slack. Code only, no AI calls. 3 new tests (31 in total).
- **Live on Streamlit Community Cloud (CR-15, milestone M6):** https://ai-customer-intelligence-version1.streamlit.app. The API key is held in the app's Secrets, not the repo. Checked from a browser not signed in to Streamlit: the sample loads all 2,618 reviews from the shipped results in seconds, with the same numbers as the case study and no AI cost.

## [0.4.1] — 2026-10-31 — First real evaluation run
### Fixed
- Anthropic calls work with SDK 2.x: `temperature` is no longer sent (the parameter was removed), and `max_tokens` is raised to 16,000 because model thinking counts towards it. Before this, every call failed and all rows came back Unclassified.
### Added
- First evaluation with a real model (claude-haiku-5-5, prompt v2, 50 reviews): **category 80.0%, sentiment 94.0%**. Quality gate fails on category. The lenient score (AI's main category is one of the human's issues) is 94%.
- `HANDOVER.md`: full project status for anyone picking it up.
### Changed
- Decision D9 and the BRD model-behaviour requirement: repeatability is now checked by the evaluation rather than enforced by temperature.

## [0.4.0] — 2026-10-30 — User acceptance testing
### Added
- UAT document (Part 10): 14 functional and 12 AI-specific test cases, with pass criteria, linked requirements and a summary sheet.
- UAT test files in `tests/uat_data/`: valid, wrong type, missing column, bad rows, over the limit, and 12 AI edge cases.
- `LOG_PROMPTS=1` writes exactly what was sent to the LLM to `data/prompt_log.txt`, so personal-data redaction can be checked (UAT-21).
- Clear error when the AI service can't label any reviews (UAT-26).
- App version and prompt version shown in the sidebar.
### Fixed
- A run where the AI failed completely is no longer saved, so a retry doesn't reload the failed results.

## [0.3.0] — 2026-10-30 — Multi-issue reviews and taxonomy v2
### Added
- Reviews get a main category plus up to 3 `other_categories` (FR-04b, decision D7 revised).
- Pain-point ranking counts secondary issues, and shows how often each was the main issue.
- Evidence marks quotes where the issue was raised as a secondary issue. The category filter matches secondary issues.
- Evaluation scores secondary issues (recall and precision) and accepts number/letter label codes.
- Labelling log (`evals/labelling-log.md`).
### Changed
- Taxonomy v2: Praise now covers only non-specific praise. Specific praise goes to the aspect praised. Crashes go to App Updates & Stability, and "old app better" goes to Design & Usability.
- Prompt `classify_v2` (v1 kept for comparison).
- Evaluation set: final human labels (11 main categories changed after review, secondary issues on 20 of 50 reviews).
- "Other" excluded from the pain-point ranking. A warning shows if more than 10% of reviews fall into it.
### Docs
- BRD v0.4. Architecture decision D7 rewritten.

## [0.2.0] — 2026-10-30 — MVP build and evaluation set
### Added
- Streamlit dashboard: upload, validation, top pain points with evidence, breakdown, trends, filters, export and opportunity suggestions.
- Pipeline: validation, personal-data redaction, batched LLM classification with schema checking and retry, aggregation, SQLite storage.
- LLM providers: Anthropic, OpenAI, and mock mode for testing without a key.
- Unit tests (pytest).
- Evaluation set of 50 Santander reviews from 2024, labelling guide, and `evals/run_eval.py`.

## [0.1.0] — 2026-10-30 — Discovery, requirements and design
### Added
- Product / Business Brief, BRD, AI Architecture & Decision Log, Project Plan, Gantt chart and Risk Register.
- Working dataset: Santander app reviews, Jan–Sep 2025 (2,618), chosen after profiling showed August 2025 alone was unrepresentative.
