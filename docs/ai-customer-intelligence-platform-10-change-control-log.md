# Change Control Log — AI Customer Intelligence Platform

> **Status:** v1.1 · 5 Nov 2026 · Started 31 Oct 2026, with changes from 30 Oct back-filled.
> **v1.1:** after mentor review — who approves each type of change (§2.1), and a *Required approver* column in the
> register (CR-19).
> Owner: Tez. Linked to the [decision log](ai-customer-intelligence-platform-03-ai-architecture-and-decision-log.md),
> [changelog](../CHANGELOG.md) and [labelling log](../evals/labelling-log.md).

---

## 1. What needs change control

Once something has been agreed, changing it needs a change record. This applies to:

| Baselined item | Where it lives |
|---|---|
| Scope and requirements | BRD (doc 02) |
| Architecture decisions | Decision log (doc 03) |
| Category taxonomy | `config/taxonomy.yaml` |
| Prompt | `prompts/classify_vN.txt` |
| Model or provider | `.env` / `app/pipeline/llm.py` |
| Evaluation labels | `evals/eval_set.xlsx` and `.csv` |
| Working dataset | `data/` |
| Schedule and milestones | Project plan (doc 04) |
| Repository history | GitHub |

Bug fixes that don't change any of these only need a changelog entry.

## 2. How a change is made

1. **Raise:** add a row below with status *Proposed*, saying what would change and why.
2. **Assess:** record the impact on scope, quality (eval scores), cost, schedule and risks.
3. **Decide:** the approver for that type of change (§2.1) approves or rejects it.
4. **Implement:** make the change. A new prompt or taxonomy gets a new version number, and the old one is kept.
5. **Verify:** re-run the tests, and re-run the evaluation if AI behaviour or labels changed.
6. **Close:** set the status and fill in where it is recorded (version, commit, documents).

**Status values:** Proposed · Approved · Rejected · Implemented · Closed.

### 2.1 Who approves which change

Roles are defined in the [Brief, §8](ai-customer-intelligence-platform-01-product-business-brief.md#8-stakeholders-and-decision-rights).

| Type of change | Approver | Also consulted |
|---|---|---|
| Scope or requirements (BRD), including new features | Product Owner | Project Sponsor if it moves the timeline or budget |
| Timeline, milestones or budget | Project Sponsor | Product Owner |
| Privacy, customer data, or the AI provider | Information Security / DPO | Product Owner |
| Category taxonomy (what the categories are) | Product Owner | Business Users, Customer Operations Lead |
| Evaluation labels | Delivery Lead | Product Owner reviews, because changes can flatter the accuracy figure (risk R07) |
| Prompt, model, architecture or code, with no requirement change | Delivery Lead | Product Owner is told if accuracy, cost or speed changes |
| Defect fixes and repository changes | Delivery Lead | — |

**In this portfolio project** the client roles are titles only, so every change
so far was decided by the Delivery Lead (Tez) on the client's behalf. The
*Required approver* column shows who would approve each one in a real
engagement. The changes that need a client approval are listed for
retrospective approval at the requirements review (C1 in the project plan).

**How the logs fit together:** the decision log says *why* a design was chosen.
The changelog says *what shipped* in each version. This log is the *control
record*: what changed, why, its impact, who approved it, and its current status.

---

## 3. Change register

The BRD's view of these changes, including which ones went beyond the original
scope, is in [BRD Appendix A](ai-customer-intelligence-platform-02-business-requirements-document.md#appendix-a--changes-since-baseline).

| CR | Date | Change | Type | Reason | Impact | Decided by | Required approver | Status | Recorded in |
|---|---|---|---|---|---|---|---|---|---|
| CR-01 | 30 Oct 2026 | Working dataset widened from Aug 2025 (837 reviews) to Jan–Sep 2025 (2,618) | Scope / data | Profiling showed August was unrepresentative: volume jumped 4–5× in July and ratings flipped to mostly 5★ | Baseline recomputed (47% of low-star reviews "Undefined"). Upload limit had to rise (CR-02). Analysis cost per run is about 3× higher. | Delivery Lead (Tez) | Product Owner | Closed | BRD v0.3 · v0.1.0 |
| CR-02 | 30 Oct 2026 | Upload limit raised from 2,000 to 5,000 rows (5 MB unchanged) | Requirement | Fit the 2,618-review working dataset with headroom | FR-02, `validate.py`, UAT-05 test file. Longer runs and higher cost per upload (risk R08). | Delivery Lead (Tez) | Product Owner | Closed | BRD v0.3 · v0.2.0 |
| CR-03 | 30 Oct 2026 | Single category per review changed to main + up to 3 secondary categories | AI behaviour | Labelling showed 20 of 50 reviews raise several issues, and single-label hid them from the ranking | Output schema, pain-point ranking, evidence display and eval metrics changed (secondary recall and precision added). | Delivery Lead (Tez) | Product Owner | Closed | D7 revised · BRD v0.4 · v0.3.0 |
| CR-04 | 30 Oct 2026 | Taxonomy v2 and prompt v2: Praise only for non-specific praise; crashes go to Stability; "old app better" goes to Design | Taxonomy / prompt | Labelling exposed ambiguous definitions | 11 eval labels changed **before** any AI output was seen. Prompt v1 kept. | Delivery Lead (Tez) | Product Owner | Closed | Labelling log · v0.3.0 |
| CR-05 | 31 Oct 2026 | Anthropic calls fixed for SDK 2.x: `temperature` no longer sent, `max_tokens` raised from 4,000 to 16,000 | Code (defect) | Every call failed (the SDK removed `temperature`). Then one batch was cut off because model thinking counts towards `max_tokens`. | No real eval was possible before this. The higher token ceiling doesn't raise cost, because only tokens actually used are billed. Led to CR-06. | Delivery Lead (Tez) | Delivery Lead | Closed | v0.4.1 · commit `0a1d43f` |
| CR-06 | 31 Oct 2026 | Decision D9 revised: "temperature 0" becomes "repeatability measured by the eval" | Architecture decision | Temperature can no longer be set (CR-05) | Repeatability is now checked by the duplicate-consistency measure (100% on both runs). | Delivery Lead (Tez) | Delivery Lead | Closed | D9 · decision history · v0.4.1 |
| CR-07 | 31 Oct 2026 | Commit author rewritten to Terence Field with the GitHub noreply email; tag v0.4.0 moved; force-pushed | Repository / privacy | Personal email was visible on a public repo | Commit IDs changed; file contents unchanged. Anyone with an old clone would need to re-clone (none known). | Delivery Lead (Tez) | Delivery Lead | Implemented | Handover to-do 1. **Open:** GitHub email-privacy settings (Tez) |
| CR-08 | 31 Oct 2026 | Main issue chosen by **outcome** (the task that went wrong), with the cause as secondary: prompt v3, taxonomy v3, labelling guide | AI behaviour / taxonomy / prompt | First eval (prompt v2): 7 of 10 category misses were main-vs-secondary swaps, and the human labels mixed outcome and cause | Category 80% → 92%, low-star category 74.2% → 93.5%, sentiment unchanged at 94%. **Quality gate (M4) passed.** Two new misses (E02, E18): see CR-11. | Delivery Lead (Tez) | Product Owner | Implemented | D17 · eval run `20261031-1410` · BRD v0.5 (FR-04) · Unreleased |
| CR-09 | 31 Oct 2026 | 6 eval labels changed to follow the outcome rule (E13, E14, E24, E41, E44, E47) | Evaluation labels | Apply CR-08 consistently to all 50 labels | Made **after** seeing AI output (risk R07). Mitigated: every change logged, old main kept as secondary, 4 agree and 2 disagree with the AI. Relabel effect about +4 points, prompt effect about +8. | Delivery Lead (Tez) | Delivery Lead (Product Owner reviews) | Implemented | Labelling log · label notes · eval set "what changed" tab |
| CR-10 | 31 Oct 2026 | Sharpen the Stability / Performance / Design boundaries in the taxonomy | Taxonomy | Remaining misses E20 ("problems loading and connecting") and E34 ("don't like this last update") | Not assessed yet. Would need taxonomy v4 and a re-run. | — | Product Owner | Proposed | Handover §4 |
| CR-11 | 31 Oct 2026 | Stop the outcome rule overriding the main praise in positive or mixed reviews | Prompt | New misses E02 and E18: a task mentioned in passing (fees, biometrics) was chosen over the main praise for ease of use | Not assessed yet. Would need prompt v4 and a re-run. | — | Delivery Lead | Proposed | Handover §4 |
| CR-12 | 31 Oct 2026 | Send LLM batches in parallel instead of one after another (5 at once), lower `max_tokens` from 16,000 to 12,000, and raise SDK retries from 2 to 6. All three can be changed in `.env` | Code / performance | Full run of 2,618 reviews took about 30 minutes against the BRD's 8-minute target (UAT-06 failed) | **Full run 30 min → 6.1 min; eval 38 s → 18.6 s.** Cost unchanged. Eval accuracy unchanged (92% / 94%). First attempt (8 at once) hit the account's 80,000 output-tokens-per-minute limit, which counts each request's `max_tokens` up front, so 78 reviews failed; settings were tuned and re-run. UAT-06 now passes. | Delivery Lead (Tez) | Delivery Lead | Implemented | `classify.py`, `llm.py`, `.env.example` · 3 new tests · UAT-06 re-test |
| CR-13 | 31 Oct 2026 | Fix the UAT dashboard defects: summary numbers follow filters (DEF-01), separate rating and problem-share charts (DEF-02), app versions sorted by number and plotted as labels with readable axes (DEF-03), 'version unknown' instead of 'vNone' (DEF-04), a date-range hint (DEF-05), sample data re-ticks when an upload is removed and a plain-English AI error (DEF-06) | Code / UI | UAT run, 31 Oct: UAT-09 and UAT-12 failed on these | Dashboard code only; no AI calls or cost. 3 new tests (25 total). UAT-09 and UAT-12 re-tested and pass; UAT-08 and UAT-26 re-checked. | Delivery Lead (Tez) | Delivery Lead | Implemented | `streamlit_app.py`, `aggregate.py` · UAT workbook (Defects sheet: all fixed) |
| CR-14 | 31 Oct 2026 | Deployment readiness: ship the finished sample results with the code (`data/precomputed/`, used only when file, model and prompt all match), and pin `requirements.txt` to the tested versions | Code / deployment | Cloud storage is wiped on every restart, so without shipped results each restart would re-run the 2,618-review analysis (6 min, ~$0.26) on the first click. Unpinned versions could install untested packages | Sample loads in about 1 second with no AI cost, and shows the same numbers as the case study (first full run). Uploads still call the AI. 1 new test (26 total) | Delivery Lead (Tez) | Delivery Lead | Implemented | `storage.py`, `data/precomputed/`, `requirements.txt`, README deploy section |
| CR-15 | 1 Nov 2026 | Deploy the MVP to Streamlit Community Cloud on 1 Nov, ahead of the planned 16 Nov and before UAT sign-off (M5). Live at https://ai-customer-intelligence-version1.streamlit.app | Schedule / deployment | The app was ready: 25 of 26 UAT cases pass and the shipped results make the demo free to run. A live link lets the last UAT case (UAT-14, a first-time user) be run on the real app | T21 and M6 done about two weeks early. M5 sign-off still open, so the live app is a pre-sign-off version. The API key is in Streamlit Secrets, not the repo. Uploads by anyone with the link are billed to the key (risk R08), so a monthly spend limit is needed | Delivery Lead (Tez) | Project Sponsor; Information Security / DPO | Implemented | Project plan (T21, M6) · README · case study v0.6 · Handover |
| CR-16 | 1 Nov 2026 | Plain-English signposting on the dashboard: answer-first headline, "How to read this page" guide, category and sentiment definitions with examples, plain-English chart hover, "?" tooltips on headline numbers and filters, data-quality numbers moved to an explained caption | Code / UI | First-look feedback on the live app: the hover box and "Low confidence (<0.6)" were hard to understand, categories like Cards weren't explained, and the page needed clearer signposting (DEF-07 to DEF-10) | Dashboard only: no AI calls, cost or eval change. The four summary numbers become two, with data quality still shown in words (transparency NFR kept). Should make UAT-14 (first-time user) easier. 2 new tests | Delivery Lead (Tez) | Delivery Lead | Implemented | `streamlit_app.py`, `aggregate.py` · UAT workbook (Defects sheet) |
| CR-17 | 1 Nov 2026 | New "Action summary" tab: ranked pain points grouped by suggested owner team (Engineering, Product, Operations) with example themes, issues raised together, app versions, trend, a quote and a next step; Markdown download | Scope / feature | Tez asked for a summary page that directs engineers on what to investigate and fix, and Product on what to look at | New scope beyond the BRD's "Must" list, done ahead of schedule. Owner mapping is new configuration (`config/teams.yaml`), kept out of the taxonomy and never sent to the AI, so labels and eval scores can't change. Trends compare share of reviews and warn when total volume moved a lot (the July 2025 jump makes raw trends misleading). Code only, no AI cost. 3 new tests (31 total) | Delivery Lead (Tez) | Product Owner | Implemented | `streamlit_app.py`, `aggregate.py`, `config/teams.yaml` · BRD v0.5 (FR-17) · README · Handover |
| CR-18 | 1 Nov 2026 | Delete saved uploads after 24 hours and keep only the shipped sample results, to meet the BRD privacy requirement | Code / privacy | Found while writing BRD Appendix A: the privacy NFR says uploads are deleted after the session or 24 hours, but saved results, including the original review text, are kept in SQLite (D14) until the app restarts or the file is deleted | Storage code only: no AI calls, cost or eval change. Saved results older than 24 hours are deleted when the page loads or an analysis starts, and SQLite's secure delete overwrites the text on disk. The shipped sample is unaffected (it reloads from `data/precomputed/` for free); an upload refreshed after 24 hours is analysed, and paid for, again. Sidebar note tells users. Week 2 "saved past analyses" will need this rule revisited. 2 new tests (33 total) | Delivery Lead (Tez) | Information Security / DPO | Implemented | `storage.py`, `streamlit_app.py` · BRD v0.5 (Privacy NFR, A.3) · Handover |
| CR-19 | 5 Nov 2026 | Client-focused documents after mentor review: client stakeholders and decision rights (Brief v0.2); BRD rewritten in business terms with technical detail moved to doc 03 (BRD v0.6); business impact per decision (doc 03 v0.2); client activities and real dates in the plan and Gantt (v0.2); business risks and spread ownership (risk register v0.2); system tests separated from business UAT (UAT workbook); approver by change type (this log v1.1); business results section (case study) | Documentation / scope presentation | Mentor review, 5 Nov: the documents were strong technically but read as the builder's view, with few client activities, approvals or business outcomes | No requirement, code or AI change. The remaining critical path is now visibly client activity (approvals, business UAT, go-live), and 7 business risks are recorded. UAT sign-off now depends on business UAT, not only system tests | Delivery Lead (Tez) | Product Owner | Implemented | Docs 01, 02, 03, 04, 05, 06, 08, 09, 10 |

### Template for a new change

```
| CR-NN | DD Mon YYYY | What changes | Type | Why | Impact on scope / quality / cost / schedule / risks | Delivery Lead | Approver from §2.1 | Proposed | Where it is recorded |
```
