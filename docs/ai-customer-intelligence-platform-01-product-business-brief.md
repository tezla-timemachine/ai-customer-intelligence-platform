# Product / Business Brief — AI Customer Intelligence Platform

> **Status:** Draft v0.2 · 5 Nov 2026 — figures marked *(assumption)* are placeholders to
> validate or replace with real data before sign-off.
> **v0.2:** after mentor review — added the client's stakeholders and who decides what (§8), and
> each assumption now says who confirms it, how, and its status (§7).

---

## 1. Problem

Our product teams receive thousands of pieces of customer feedback every
month across four channels — app/marketplace reviews, support tickets,
survey responses (NPS/CSAT free text) and in-product feedback comments.

Today this feedback is reviewed manually. As a result:

- **Most feedback is never read.** Teams sample a fraction of it, so
  recurring problems can go unnoticed for weeks.
- **Analysis is slow.** Insights arrive in monthly or quarterly reviews,
  long after the problem first appeared.
- **Tagging is inconsistent.** Different people label the same issue in
  different ways, so trends can't be compared reliably over time.
- **Prioritisation leans on anecdote.** Decisions are swayed by the
  loudest customer or the most recent escalation rather than by the true
  frequency and severity of a problem.
- **Evidence gets lost.** By the time an insight reaches a roadmap
  discussion, the underlying customer quotes are buried in spreadsheets.

**Problem statement:** Product teams cannot reliably identify, quantify
and evidence the most important customer problems from the volume of
feedback they receive, which slows and weakens product prioritisation.

---

## 2. Target Users

| User | Role in the product | Priority |
|---|---|---|
| **Product Manager** | Uses insights to understand pain points and decide what to prioritise; reviews evidence behind each theme | **Primary** |
| Head of Product | Views top issues across products to inform roadmap and resourcing | Secondary |
| Product Operations | Owns the feedback process; uploads data, maintains the category taxonomy | Secondary |
| Customer Success Manager | Checks which issues affect which customer segments; feeds back to accounts | Secondary |

**Primary persona:** a Product Manager responsible for one product area,
who needs to walk into a prioritisation meeting with a ranked, evidenced
view of what customers are struggling with — without spending days
reading feedback first.

---

## 3. Current Process

1. Feedback is exported from source tools (helpdesk, survey platform,
   review sites) into spreadsheets, usually monthly.
2. A PM or Product Ops analyst reads a sample and tags each item by hand.
3. Tags are counted in the spreadsheet to find the most common issues.
4. Findings are summarised in slides, with a few quotes copied across.
5. Findings are discussed in a prioritisation meeting.

**Pain points in this process:** time-consuming *(assumption: 1–2 days per
PM per month)*, partial coverage, inconsistent tagging between people,
slow detection of new issues, and weak traceability back to evidence.

---

## 4. Is AI the Right Solution?

The core difficulty is **understanding unstructured language at volume** —
customers describe the same problem in many different ways, mix praise
with complaints, raise several issues in one comment, and use sarcasm.

| Option | Assessment |
|---|---|
| Keep manual tagging | Accurate in small volumes, but doesn't scale and stays inconsistent |
| Keyword / rules-based tagging | Cheap and predictable, but brittle — misses paraphrases, mixed sentiment and sarcasm |
| Train a traditional ML classifier | Needs a large labelled dataset we don't have; slower to change categories |
| **LLM with a controlled taxonomy** | Handles varied language and nuance without training data; categories can be updated by editing the taxonomy |

**Conclusion:** AI is appropriate for the *language-understanding* steps
— classifying, judging sentiment, extracting themes and interpreting
problems. It is **not** appropriate for counting, calculating percentages,
ranking or charting, which deterministic code does faster, cheaper and
with guaranteed accuracy. Prioritisation decisions remain with humans; AI
provides evidenced input, not the decision.

---

## 5. Proposed AI Opportunity

AI improves the existing process at three specific points:

1. **Tagging (step 2):** classify every feedback item — not a sample — into
   a fixed product-issue taxonomy, with sentiment, consistently.
2. **Theme detection (step 3):** group related feedback into recurring
   themes and pain points, including ones not yet in the taxonomy.
3. **Evidence linking (step 4):** attach representative customer quotes to
   every theme, so each insight is traceable to real feedback.

As a stretch within the MVP, AI may *suggest* possible product
opportunities from the top pain points, clearly labelled as suggestions
for the PM to evaluate.

---

## 6. Business Value & Success Metrics

| Outcome | Metric | Target *(assumption)* |
|---|---|---|
| Reduce manual analysis time | Hours per PM per monthly feedback review | From ~12 hours to under 2 hours |
| Increase coverage | % of received feedback analysed | From sampled to 100% |
| Identify recurring issues faster | Time from feedback arriving to theme being visible | From monthly review to same day as upload |
| Trustworthy classification | Category accuracy vs human-labelled evaluation set | ≥ 85% |
| Trustworthy sentiment | Sentiment accuracy vs evaluation set, incl. mixed | ≥ 85% |
| Traceable insights | % of surfaced themes linked to supporting quotes | 100% |
| Support prioritisation | Platform output used in prioritisation meetings | Used in next 2 consecutive cycles by pilot PMs |

---

## 7. Key Assumptions to Validate

Each assumption has a client owner who confirms it. Roles are defined in §8.
Status as of 5 Nov 2026.

| # | Assumption | How it will be confirmed | Confirmed by | Status |
|---|---|---|---|---|
| A1 | PMs spend about 1–2 days (~12 hours) a month on manual feedback review | Ask 3–5 PMs to log time for one monthly review | Product Owner, with the pilot PMs | **Open.** The ~12 hours in §6 is still an estimate |
| A2 | Feedback can be exported to CSV with at least text, date, rating and customer type | Export one month from each of the four channels | Customer Operations Lead (support tickets); Product Owner (reviews, surveys) | **Partly confirmed:** app-store reviews export cleanly (2,618 reviews used). Support tickets, surveys and in-app comments not yet tried |
| A3 | A fixed taxonomy of about 8–12 categories covers most feedback | Run the taxonomy over real feedback and check the "Other" share | Product Owner | **Confirmed for app reviews:** 12 categories, 1.9% "Other". Other channels not yet tested |
| A4 | PMs will trust AI-generated categories if every theme shows its evidence | Business UAT with pilot PMs (doc 08), then use in a real prioritisation meeting | Product Owner, with the pilot PMs | **Open.** First business-user test (UAT-14) in progress |
| A5 | Sending feedback text to an external AI provider is acceptable once personal data is removed | Data-protection review of the redaction, the provider's terms and the 24-hour deletion | Information Security / Data Protection Officer | **Open.** Built to support approval (redaction, no training on data, deletion after 24 hours) but not yet reviewed |
| A6 | The targets in §6 are the right measures of success | Review §6 at the requirements sign-off | Project Sponsor | **Open** |

---

## 8. Stakeholders and Decision Rights

The client is a retail bank's digital team. People are named by **role title
only**. The Delivery Lead is the supplier side (the person building the
platform); every other role is on the client side.

| Role | Interest | Involvement |
|---|---|---|
| **Project Sponsor** (e.g. Head of Digital) | Business case, budget, timeline | Approves scope, budget and timeline changes; gives final go-live approval |
| **Product Owner** (e.g. Head of Product, mobile app) | That the tool helps PMs prioritise | Owns requirements and priorities; approves requirement changes; signs off UAT |
| **Business Users** (pilot Product Managers) | A faster, evidenced view of customer problems | Take part in prototype review and run business UAT; give feedback after go-live |
| **Information Security / Data Protection Officer** | Customer data is handled lawfully and safely | Approves privacy and data-handling changes and the use of an external AI provider |
| **Customer Operations Lead** | Support issues are visible to Product | Supplies support-ticket exports; owns the Operations items in the Action summary |
| **Engineering Lead** (client) | Issues reach Engineering with enough detail to act on | Reviews the Action summary format; owns the Engineering items |
| **Delivery Lead / PM** (Tez, supplier) | Delivering the platform on time and to quality | Plans and builds; makes technical design decisions; raises changes for approval |

### Who decides what

| Decision | Decides | Consulted |
|---|---|---|
| Scope, budget and timeline | Project Sponsor | Product Owner, Delivery Lead |
| Requirements and their priority | Product Owner | Business Users, Delivery Lead |
| Categories in the taxonomy | Product Owner | Business Users, Customer Operations Lead |
| Privacy, data handling and the AI provider | Information Security / DPO | Delivery Lead |
| Technical design (model, architecture, tools) | Delivery Lead | Information Security for anything touching data |
| UAT sign-off | Product Owner | Business Users |
| Go-live | Project Sponsor | Product Owner, Information Security |

These rights are used throughout: approvals in the change control log
(doc 10), risk owners (doc 06), client milestones in the plan (doc 04) and
UAT sign-off (doc 08).
