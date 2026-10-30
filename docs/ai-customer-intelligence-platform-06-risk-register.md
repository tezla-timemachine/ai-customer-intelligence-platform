# Risk Register — AI Customer Intelligence Platform

> **Status:** Draft v0.1 · Covers challenge Part 7.
> Reviewed at each milestone (M2–M6). Linked to the
> [project plan](ai-customer-intelligence-platform-04-project-plan.md) and
> [architecture decisions](ai-customer-intelligence-platform-03-ai-architecture-and-decision-log.md).

**Scoring:** Probability and Impact are each Low (1), Medium (2) or High (3).
Score = P × I. **6–9 = High priority**, 3–4 = Medium, 1–2 = Low.

---

## 1. Summary Heat Map

| | **Low impact** | **Medium impact** | **High impact** |
|---|---|---|---|
| **High probability** | | R04, R07 | R01 |
| **Medium probability** | | R06, R08, R10, R12 | R02, R03, R05, R09 |
| **Low probability** | | R11 | |

---

## 2. Register

| ID | Risk | Type | P | I | Score | Mitigation | Early warning sign | Owner | Status |
|---|---|---|---|---|---|---|---|---|---|
| **R01** | **LLM mislabels reviews that contain sarcasm, mixed sentiment or several issues** (e.g. "Great, another update that logs me out") | AI quality | H | H | **9** | "Mixed" sentiment defined in the prompt with examples; eval set deliberately includes sarcastic and multi-issue reviews; accuracy reported separately for them; prompt v2 targets the failures found | Mixed/sarcastic accuracy well below overall accuracy in the eval run | PM | Open |
| **R02** | **AI accuracy misses the 85% quality gate (M4)** | AI quality | M | H | **6** | Start with a small model but allow a larger-model run; failure analysis + prompt v2 day built into plan; fallback options agreed in advance (larger model, simpler taxonomy, or launch with the gap documented) | First eval run below 80% | PM | Open |
| **R03** | **PM over-trusts AI output and acts on a wrong insight** (automation bias) | Product / AI | M | H | **6** | Every pain point shows real quotes (D11); AI labels clearly marked; low-confidence items flagged; unclassified count always visible; PM decides priorities | UAT testers repeat insights without opening the evidence | PM | Open |
| **R04** | **Inconsistent categories for similar reviews** (same issue labelled "Login" one time, "Security Checks" the next) | AI quality | H | M | **6** | Controlled taxonomy with definitions and boundary examples (D4); temperature 0 (D9); eval checks near-duplicate reviews get the same label | Eval confusion matrix shows two categories frequently swapped | PM | Open |
| **R05** | **Sensitive customer data is sent to the model provider** (account numbers, phone numbers in review text) | Privacy / compliance | M | H | **6** | Regex redaction before any LLM call (D10, FR-03); test cases with fake card/phone numbers in functional testing; provider chosen with no training on API data | Redaction test finds a pattern that slips through | PM | Open |
| **R06** | **Skewed data produces misleading insights** — July 2025 jump in volume and 5★ ratings, likely from in-app rating prompts | Data | M | M | 4 | Analysis covers Jan–Sep, not one month; dashboard shows monthly volume and rating trend so the shift is visible; caveat stated in the case study | Pain-point ranking changes sharply when July–Aug are included vs excluded | PM | Open |
| **R07** | **Evaluation set is biased because one person labels it** | AI evaluation | H | M | **6** | Write labelling rules before labelling; label before seeing any AI output; re-label 10 reviews a few days later and measure self-agreement; ask the mentor to label a sample if possible | Self-agreement below 85% | PM | Open |
| **R08** | **Large files cause excessive processing time or cost** | Cost / performance | M | M | 4 | Batching of ~20 reviews (D6); 5,000-row upload limit; results saved so refreshes don't re-run (D14); cost and latency measured in T17 | One run costs more than £1 or takes > 8 minutes | PM | Open |
| **R09** | **AI integration takes longer than planned and delays launch** (critical path) | Delivery | M | H | **6** | 20-review API spike during model selection (T5) to prove the integration early; keep the first version simple (no streaming, no async) | Spike not working by end of Mon 2 Nov | PM | Open |
| **R10** | **Scope creep** — competitor comparison across banks, reply analysis, multi-label, trend alerts | Delivery | M | M | 4 | Out-of-scope list in BRD §9; new ideas go to a v2 backlog, not the current plan; taxonomy frozen at M2 | Tasks appear that aren't in the schedule | PM | Open |
| **R11** | **Dataset licensing / terms challenge** — third-party scrape of Google Play with no stated licence | Legal | L | M | 2 | Non-commercial portfolio use only; full dataset not republished; only small slice and eval set in repo; source credited; data sourcing section in BRD §8 | Takedown request or licence change on Hugging Face | PM | Open |
| **R12** | **Model or provider changes break the pipeline or change results** (new model version, price change, outage) | Technical | M | M | 4 | Model and prompt version recorded per run; eval re-run on any model change; batch retry on failures; saved results remain viewable during an outage | Eval scores shift with no prompt change | PM | Open |

---

## 3. Top Risks — Why They Matter

**R01 – Mislabelling nuanced reviews.** This is the core AI risk. A banking
review like *"Love the app, shame it logs me out every five minutes"* is both
praise and a real problem. If the AI calls it positive, a genuine pain point
disappears from the ranking. This is why "mixed" sentiment exists and why
it gets its own accuracy figure and its own UAT case.

**R03 – Over-trust.** A dashboard that looks confident can be wrong
confidently. The product design answer is that *nothing appears without
evidence*: every pain point links to the actual customer words, and the
dashboard is honest about what it couldn't classify.

**R07 – A biased evaluation set.** The accuracy figure is only as good as
the labels it's measured against. With one labeller, the mitigation is
process: rules written first, labels done before seeing AI output, and a
self-agreement check.

---

## 4. Review Log

| Date | Milestone | Changes |
|---|---|---|
| 30 Oct 2026 | Draft | Register created with 12 risks |
