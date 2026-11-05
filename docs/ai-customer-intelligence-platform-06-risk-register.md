# Risk Register — AI Customer Intelligence Platform

> **Status:** Draft v0.2 · 5 Nov 2026 · Covers challenge Part 7.
> **v0.2:** after mentor review — 7 business and client risks added (R13–R19), owners spread across the client
> roles in the [Brief, §8](ai-customer-intelligence-platform-01-product-business-brief.md#8-stakeholders-and-decision-rights)
> instead of all with the PM, and statuses updated from the build and evaluation (CR-19).
> Reviewed at each milestone (M2–M6). Linked to the
> [project plan](ai-customer-intelligence-platform-04-project-plan.md) and
> [architecture decisions](ai-customer-intelligence-platform-03-ai-architecture-and-decision-log.md).

**Scoring:** Probability and Impact are each Low (1), Medium (2) or High (3).
Score = P × I. **6–9 = High priority**, 3–4 = Medium, 1–2 = Low.

---

## 1. Summary Heat Map

Open risks only (R02 and R09 are closed).

| | **Low impact** | **Medium impact** | **High impact** |
|---|---|---|---|
| **High probability** | | R04, R07 | R01 |
| **Medium probability** | | R06, R08, R10, R12, R14, R16, R19 | R03, R05, R13, R15, R17, R18 |
| **Low probability** | | R11 | |

### Owners

| Owner | Risks |
|---|---|
| Project Sponsor | R08, R11, R13, R16, R19 |
| Product Owner | R03, R06, R10, R14, R15, R17 |
| Information Security / DPO | R05, R18 |
| Delivery Lead | R01, R02, R04, R07, R09, R12 |

Since the build is done, the highest open risks are now about the client
and the business (R13, R15, R17, R18), not the AI.

---

## 2. Register

| ID | Risk | Type | P | I | Score | Mitigation | Early warning sign | Owner | Status |
|---|---|---|---|---|---|---|---|---|---|
| **R01** | **LLM mislabels reviews that contain sarcasm, mixed sentiment or several issues** (e.g. "Great, another update that logs me out") | AI quality | H | H | **9** | "Mixed" sentiment defined in the prompt with examples; eval set deliberately includes sarcastic and multi-issue reviews; accuracy reported separately for them; prompt v2 targets the failures found | Mixed/sarcastic accuracy well below overall accuracy in the eval run | Delivery Lead | Monitoring: sentiment 94% on the eval set, mixed reviews included |
| **R02** | **AI accuracy misses the 85% quality gate (M4)** | AI quality | M | H | **6** | Start with a small model but allow a larger-model run; failure analysis + prompt v2 day built into plan; fallback options agreed in advance (larger model, simpler taxonomy, or launch with the gap documented) | First eval run below 80% | Delivery Lead | **Closed** 31 Oct: gate passed, category 92%, sentiment 94% |
| **R03** | **PM over-trusts AI output and acts on a wrong insight** (automation bias) | Product / AI | M | H | **6** | Every pain point shows real quotes (D11); AI labels clearly marked; low-confidence items flagged; unclassified count always visible; PM decides priorities | UAT testers repeat insights without opening the evidence | Product Owner | Open: to check in business UAT |
| **R04** | **Inconsistent categories for similar reviews** (same issue labelled "Login" one time, "Security Checks" the next) | AI quality | H | M | **6** | Controlled taxonomy with definitions and boundary examples (D4); repeatability measured by the eval (D9); eval checks near-duplicate reviews get the same label | Eval confusion matrix shows two categories frequently swapped | Delivery Lead | Monitoring: duplicates 100% consistent; two full runs agreed on 95.5% of main categories |
| **R05** | **Sensitive customer data is sent to the model provider** (account numbers, phone numbers in review text) | Privacy / compliance | M | H | **6** | Regex redaction before any LLM call (D10, FR-03); test cases with fake card/phone numbers in functional testing; provider chosen with no training on API data | Redaction test finds a pattern that slips through | Information Security / DPO | Open: redaction tested (UAT AI cases); security review C4 pending |
| **R06** | **Skewed data produces misleading insights** — July 2025 jump in volume and 5★ ratings, likely from in-app rating prompts | Data | M | M | 4 | Analysis covers Jan–Sep, not one month; dashboard shows monthly volume and rating trend so the shift is visible; caveat stated in the case study | Pain-point ranking changes sharply when July–Aug are included vs excluded | Product Owner | Open: cause of the July jump unknown; trends warn when volume changes (CR-17) |
| **R07** | **Evaluation set is biased because one person labels it** | AI evaluation | H | M | **6** | Write labelling rules before labelling; label before seeing any AI output; re-label 10 reviews a few days later and measure self-agreement; ask the mentor to label a sample if possible | Self-agreement below 85% | Delivery Lead | Open: 6 labels changed after seeing AI output, all logged (CR-09) |
| **R08** | **Large files cause excessive processing time or cost** | Cost / performance | M | M | 4 | Batching of ~20 reviews (D6); 5,000-row upload limit; results saved so refreshes don't re-run (D14); cost and latency measured in T17 | One run costs more than £1 or takes > 8 minutes | Project Sponsor | Monitoring: $0.26 per full run, 6.1 min. Anyone with the demo link can trigger paid uploads: monthly spend limit to set |
| **R09** | **AI integration takes longer than planned and delays launch** (critical path) | Delivery | M | H | **6** | 20-review API spike during model selection (T5) to prove the integration early; keep the first version simple (no streaming, no async) | Spike not working by end of Mon 2 Nov | Delivery Lead | **Closed** 31 Oct: integration done and working |
| **R10** | **Scope creep** — competitor comparison across banks, reply analysis, multi-label, trend alerts | Delivery | M | M | 4 | Out-of-scope list in BRD §9; new ideas go to a v2 backlog, not the current plan; taxonomy frozen at M2 | Tasks appear that aren't in the schedule | Product Owner | Occurred, controlled: two additions (CR-03, CR-17) went through change control, see BRD Appendix A |
| **R11** | **Dataset licensing / terms challenge** — third-party scrape of Google Play with no stated licence | Legal | L | M | 2 | Non-commercial portfolio use only; full dataset not republished; only small slice and eval set in repo; source credited; data sourcing section in BRD §8 | Takedown request or licence change on Hugging Face | Project Sponsor | Open |
| **R12** | **Model or provider changes break the pipeline or change results** (new model version, price change, outage) | Technical | M | M | 4 | Model and prompt version recorded per run; eval re-run on any model change; batch retry on failures; saved results remain viewable during an outage | Eval scores shift with no prompt change | Delivery Lead | Open: SDK change already hit once (CR-05), caught by the eval |
| **R13** | **Client feedback and approvals arrive late** (requirements approval, prototype review, UAT) | Client / delivery | M | H | **6** | Book the prototype review and UAT sessions now; send short review packs (BRD §11–12, a 2-minute demo); agree a 2-working-day turnaround; escalate to the Sponsor if missed | No requirements approval (M1) by Mon 9 Nov | Project Sponsor | Open: M1 in review |
| R14 | **Requirements change after approval** | Scope | M | M | 4 | Requirements baselined; every change goes through change control with the right approver (doc 10, §2.1); impact on date and cost stated before approval | Change requests after M1 that move M5 or M8 | Product Owner | Open |
| **R15** | **Low adoption: PMs keep their manual process** | Adoption / business value | M | H | **6** | Pilot PMs shape it at the prototype review and UAT; answer-first page and Action summary fit their meetings; handover session; use tracked over 2 prioritisation cycles (BRD §11) | Pilot PMs don't open it in the first cycle after go-live | Product Owner | Open |
| R16 | **Stakeholders disagree with the findings or with who owns an issue** (e.g. Engineering disputes that Stability is the top problem) | Stakeholder | M | M | 4 | Every finding shows real quotes and counts; team owners agreed with the Engineering Lead and Customer Operations Lead at the prototype review; decision rights in Brief §8 | Teams contest the ranking or reassign items in meetings | Project Sponsor | Open |
| **R17** | **Business UAT is delayed or finds major issues** | Client / delivery | M | H | **6** | Short scripted UAT (under an hour per tester); live link, so no setup; a day reserved for fixes (T24); first-time-user test already run by the mentor (BUAT-01) | Pilot PMs not booked by Tue 10 Nov | Product Owner | Open |
| **R18** | **Security review delays or blocks go-live** (use of an external AI provider) | Compliance | M | H | **6** | Start the review early (C4, 9 Nov) with an evidence pack: redaction tests, provider's no-training terms, 24-hour deletion (CR-18); fallback: public data only | Questions on data residency or contract terms | Information Security / DPO | Open |
| R19 | **The business benefit is not proven** (the 12-hours-to-2 time saving is an estimate) | Business value | M | M | 4 | Pilot PMs log time before and after for one cycle (Brief A1, BRD §11); results reported honestly in the case study, including if smaller | No baseline time measured before go-live | Project Sponsor | Open |

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

**R15 – Low adoption.** The tool can be accurate and still fail if PMs
keep doing it by hand. Adoption is the real measure of success (BRD §11),
so pilot PMs are involved before go-live, not after it.

**R13 – Late client feedback.** With the build finished, every remaining
critical task needs a client role. Approvals that slip move go-live day for
day.

**R07 – A biased evaluation set.** The accuracy figure is only as good as
the labels it's measured against. With one labeller, the mitigation is
process: rules written first, labels done before seeing AI output, and a
self-agreement check.

---

## 4. Review Log

| Date | Milestone | Changes |
|---|---|---|
| 30 Oct 2026 | Draft | Register created with 12 risks |
| 5 Nov 2026 | Mentor review | R13–R19 added (client and business risks); owners spread across client roles; R02 and R09 closed; statuses updated |
