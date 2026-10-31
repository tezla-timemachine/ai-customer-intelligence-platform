# Change Control Log — AI Customer Intelligence Platform

> **Status:** v1.0 · Started 31 Oct 2026, with changes from 30 Oct back-filled.
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
3. **Decide:** Tez approves or rejects. Tell the mentor about scope or schedule changes.
4. **Implement:** make the change. A new prompt or taxonomy gets a new version number, and the old one is kept.
5. **Verify:** re-run the tests, and re-run the evaluation if AI behaviour or labels changed.
6. **Close:** set the status and fill in where it is recorded (version, commit, documents).

**Status values:** Proposed · Approved · Rejected · Implemented · Closed.

**How the logs fit together:** the decision log says *why* a design was chosen.
The changelog says *what shipped* in each version. This log is the *control
record*: what changed, why, its impact, who approved it, and its current status.

---

## 3. Change register

| CR | Date | Change | Type | Reason | Impact | Decided by | Status | Recorded in |
|---|---|---|---|---|---|---|---|---|
| CR-01 | 30 Oct 2026 | Working dataset widened from Aug 2025 (837 reviews) to Jan–Sep 2025 (2,618) | Scope / data | Profiling showed August was unrepresentative: volume jumped 4–5× in July and ratings flipped to mostly 5★ | Baseline recomputed (47% of low-star reviews "Undefined"). Upload limit had to rise (CR-02). Analysis cost per run is about 3× higher. | Tez | Closed | BRD v0.3 · v0.1.0 |
| CR-02 | 30 Oct 2026 | Upload limit raised from 2,000 to 5,000 rows (5 MB unchanged) | Requirement | Fit the 2,618-review working dataset with headroom | FR-02, `validate.py`, UAT-05 test file. Longer runs and higher cost per upload (risk R08). | Tez | Closed | BRD v0.3 · v0.2.0 |
| CR-03 | 30 Oct 2026 | Single category per review changed to main + up to 3 secondary categories | AI behaviour | Labelling showed 20 of 50 reviews raise several issues, and single-label hid them from the ranking | Output schema, pain-point ranking, evidence display and eval metrics changed (secondary recall and precision added). | Tez | Closed | D7 revised · BRD v0.4 · v0.3.0 |
| CR-04 | 30 Oct 2026 | Taxonomy v2 and prompt v2: Praise only for non-specific praise; crashes go to Stability; "old app better" goes to Design | Taxonomy / prompt | Labelling exposed ambiguous definitions | 11 eval labels changed **before** any AI output was seen. Prompt v1 kept. | Tez | Closed | Labelling log · v0.3.0 |
| CR-05 | 31 Oct 2026 | Anthropic calls fixed for SDK 2.x: `temperature` no longer sent, `max_tokens` raised from 4,000 to 16,000 | Code (defect) | Every call failed (the SDK removed `temperature`). Then one batch was cut off because model thinking counts towards `max_tokens`. | No real eval was possible before this. The higher token ceiling doesn't raise cost, because only tokens actually used are billed. Led to CR-06. | Tez | Closed | v0.4.1 · commit `0a1d43f` |
| CR-06 | 31 Oct 2026 | Decision D9 revised: "temperature 0" becomes "repeatability measured by the eval" | Architecture decision | Temperature can no longer be set (CR-05) | Repeatability is now checked by the duplicate-consistency measure (100% on both runs). | Tez | Closed | D9 · decision history · v0.4.1 |
| CR-07 | 31 Oct 2026 | Commit author rewritten to Terence Field with the GitHub noreply email; tag v0.4.0 moved; force-pushed | Repository / privacy | Personal email was visible on a public repo | Commit IDs changed; file contents unchanged. Anyone with an old clone would need to re-clone (none known). | Tez | Implemented | Handover to-do 1. **Open:** GitHub email-privacy settings (Tez) |
| CR-08 | 31 Oct 2026 | Main issue chosen by **outcome** (the task that went wrong), with the cause as secondary: prompt v3, taxonomy v3, labelling guide | AI behaviour / taxonomy / prompt | First eval (prompt v2): 7 of 10 category misses were main-vs-secondary swaps, and the human labels mixed outcome and cause | Category 80% → 92%, low-star category 74.2% → 93.5%, sentiment unchanged at 94%. **Quality gate (M4) passed.** Two new misses (E02, E18): see CR-11. | Tez | Implemented | D17 · eval run `20261031-1410` · Unreleased |
| CR-09 | 31 Oct 2026 | 6 eval labels changed to follow the outcome rule (E13, E14, E24, E41, E44, E47) | Evaluation labels | Apply CR-08 consistently to all 50 labels | Made **after** seeing AI output (risk R07). Mitigated: every change logged, old main kept as secondary, 4 agree and 2 disagree with the AI. Relabel effect about +4 points, prompt effect about +8. | Tez | Implemented | Labelling log · label notes · eval set "what changed" tab |
| CR-10 | 31 Oct 2026 | Sharpen the Stability / Performance / Design boundaries in the taxonomy | Taxonomy | Remaining misses E20 ("problems loading and connecting") and E34 ("don't like this last update") | Not assessed yet. Would need taxonomy v4 and a re-run. | — | Proposed | Handover §4 |
| CR-11 | 31 Oct 2026 | Stop the outcome rule overriding the main praise in positive or mixed reviews | Prompt | New misses E02 and E18: a task mentioned in passing (fees, biometrics) was chosen over the main praise for ease of use | Not assessed yet. Would need prompt v4 and a re-run. | — | Proposed | Handover §4 |
| CR-12 | 31 Oct 2026 | Send LLM batches in parallel instead of one after another | Code / performance | Full run of 2,618 reviews took about 30 minutes against the BRD's 8-minute target | Not assessed yet. Needs care with rate limits (risk R08) and keeping a failed batch isolated. Cost unchanged. | — | Proposed | Case study §10 |

### Template for a new change

```
| CR-NN | DD Mon YYYY | What changes | Type | Why | Impact on scope / quality / cost / schedule / risks | Tez | Proposed | Where it is recorded |
```
