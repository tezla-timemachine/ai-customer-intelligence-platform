# Changelog

All notable changes to the AI Customer Intelligence Platform.
Format based on [Keep a Changelog](https://keepachangelog.com/). Versions follow
[semantic versioning](https://semver.org/): MAJOR.MINOR.PATCH.

Document versions (e.g. BRD v0.4) are tracked in each document's status line.
Prompt versions live in `prompts/` and are recorded against every analysis run
and evaluation result.

## [Unreleased]
- First evaluation run with a real LLM (milestone M4)
- Prompt v3 based on failure analysis
- Deployment to Streamlit Community Cloud (milestone M6)

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
