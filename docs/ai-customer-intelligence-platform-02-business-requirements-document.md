# Business Requirements Document — AI Customer Intelligence Platform (MVP)

> **Status:** v0.6 · 5 Nov 2026 · Covers challenge Parts 2 (MVP definition) and 3 (BRD).
> Builds on [Product / Business Brief](ai-customer-intelligence-platform-01-product-business-brief.md). Figures marked *(assumption)*
> are placeholders to validate during build and evaluation.
>
> **v0.2:** grounded in a real dataset — UK banking app reviews — with a
> banking-specific taxonomy and a measured baseline from an existing topic model.
> **v0.3:** working dataset widened from one month (Aug 2025, 837 reviews) to
> Jan–Sep 2025 (2,618 reviews) after finding August was unrepresentative.
> **v0.4:** after labelling the evaluation set — reviews with several issues now get a main
> category plus up to 3 secondary categories; Praise narrowed to non-specific praise.
> **v0.5:** baselined. FR-04 updated to the outcome rule (CR-08), FR-17 Action summary added (CR-17), and
> [Appendix A](#appendix-a--changes-since-baseline) records every change since baseline, what was outside the
> original scope, and the one deviation found (privacy retention), now fixed by CR-18.
> **v0.6:** after mentor review, refocused on what the client needs. Technical detail (how AI and code
> split the work, the processing pipeline, the output format, model settings) moved to the
> [architecture document](ai-customer-intelligence-platform-03-ai-architecture-and-decision-log.md). No requirement changed in substance. Added expected
> business outcomes (§11) and approvals by client role (§12) (CR-19).

---

## 1. Product Objective

Give a Product Manager a ranked, evidenced view of what customers are
struggling with, produced from **every** feedback item in an uploaded file,
in minutes instead of days.

The MVP succeeds if a PM can upload a period of app reviews and walk into a
prioritisation meeting with:

- the top pain points, ranked by how often and how negatively they come up
- real customer quotes behind each one
- trust that the tagging is consistent (≥ 85% agreement with human labels)

---

## 2. MVP Scope (Part 2)

### 2.1 Dataset

**Source:** [`pcatarino88/banking-app-reviews-data`](https://huggingface.co/datasets/pcatarino88/banking-app-reviews-data)
(Hugging Face) — 703,563 public Google Play reviews of six UK banking apps,
January 2018 to September 2025.

| App | Reviews |
|---|---|
| Revolut | 254,287 |
| Barclays | 205,758 |
| Lloyds | 114,260 |
| Santander | 69,409 |
| HSBC | 38,622 |
| Monzo | 21,227 |

**MVP working dataset:** Santander, **1 January – 4 September 2025 —
2,618 reviews** (1,452 five-star; 934 at three stars or below).

Santander was chosen because it has a manageable volume, detailed
complaints, and a high reply rate from the bank (83%), which is useful for
later iterations.

**Why nine months, not one:** the first slice tried was August 2025 alone
(837 reviews). Profiling showed August was unrepresentative:

| Period (2025) | Reviews per month | Avg stars | 3★ or below |
|---|---|---|---|
| Jan – Jun | 95 – 228 | 2.0 – 2.8 | 62 – 81% |
| Jul | 746 | 4.4 | 16% |
| Aug | 837 | 4.4 | 15% |

Volume jumped 4–5× in July and ratings flipped from mostly negative to
mostly positive. The likely cause is the app starting to prompt satisfied
users for ratings — unconfirmed, but a pattern a PM should question rather
than read as "the app got better". Using January–September gives both
complaint-heavy and praise-heavy months, a fairer test of the AI, and a
real trend for the dashboard to show.

### 2.2 The baseline we have to beat

The dataset already contains labels from an earlier automated approach — a
traditional topic model with 7 topics. It is a ready-made comparison:

| Measure (Santander, Jan–Sep 2025) | Existing topic model |
|---|---|
| Reviews left **"Undefined"** | **1,369 of 2,618 (52%)** |
| **Low-star reviews (≤ 3★) left "Undefined"** | **436 of 934 (47%)** |

The second figure is the one that matters to a PM: nearly half of the
reviews that contain an actual problem were not classified. Examples it
missed include *"Unable to logon, put in security number and it just sits
doing nothing"* and a complaint about being made to photograph a driving
licence to keep using the app.

**Honest framing:** many "Undefined" items are short positive reviews where
little is lost. The MVP is judged on whether it classifies the *problem*
reviews accurately, not on making the Undefined number smaller.

### 2.3 Input

One CSV uploaded by the user. Required and optional columns, mapped to the
dataset:

| Platform field | Required | Dataset column | Example |
|---|---|---|---|
| `feedback` | Yes | `review_text` | "App crashes every time I open it" |
| `date` | Yes | `review_date` | 2025-03-14 |
| `rating` | No | `score` | 1–5 |
| `segment` | No | `app_version_detail` | 24.0 |
| `id` | No | `review_id` | 1042 |

`segment` replaces the generic "customer type" from the brief. Public app
reviews carry no customer type, but app version is a real, useful segment —
it answers *"did the latest release make things worse?"*

The older model's labels (`topic_label_ALL`, `review_sentiment_label`) are
**not** inputs to the AI. They are kept aside for the baseline comparison only.

### 2.4 What the MVP does

For **every** review in the uploaded file, the MVP:

- sorts it into a product-issue category, plus up to 3 other issues it raises
- judges whether the customer is positive, negative, neutral or mixed
- sums up its main point in a short theme and, for complaints, the underlying problem

Then, across the whole file, it:

- ranks the biggest pain points by how often and how negatively they come up
- shows real customer quotes behind each one
- lets the PM filter by category, sentiment, date and app version, and see trends
- groups the pain points by owning team for hand-off (Action summary, FR-17)
- can suggest product opportunities, clearly labelled as AI suggestions
- exports every review with its labels

**Business rule:** AI reads and labels the reviews; every number, ranking and
chart is calculated exactly. So the counts a PM quotes in a meeting are
always right, the same file always gives the same counts, and the AI never
makes the prioritisation decision. How the work is split between AI and
code is in the [architecture document, §1.1](ai-customer-intelligence-platform-03-ai-architecture-and-decision-log.md#11-what-ai-does-and-what-code-does).

### 2.5 Category taxonomy (controlled list)

The AI must choose from this fixed list; it may not invent categories.
Built from reading the 2025 Santander reviews. The list is owned by the
Product Owner ([Brief §8](ai-customer-intelligence-platform-01-product-business-brief.md#8-stakeholders-and-decision-rights)).

| Category | Covers | Example from the data |
|---|---|---|
| Login & Access | Can't log in, passwords, biometrics, locked out | "Unable to logon, put in security number and it just sits doing nothing" |
| Identity & Security Checks | ID verification, selfies, security codes, fraud blocks | "have to take photos of my self and driving licence to authorise my account" |
| App Updates & Stability | Forced updates, crashes, install failures | "has to be updated again before I can access my account. But it fails to install" |
| Performance | Slow loading, lag, timeouts | "New 2024 app is slow to open" |
| Payments & Transfers | Sending money, payees, standing orders, pending payments | "Cant edit payees or standing orders" |
| Cards | Card controls, lost/stolen, Apple/Google Pay | — |
| Design & Usability | Layout, navigation, hard to find things | "only half the screen can show accounts info while the rest is wasted" |
| Missing Feature | Requests for something the app doesn't do | "No payment notifications" |
| Fees & Charges | Fees, interest, exchange rates | — |
| Customer Support | Experience with branches, phone or chat support | — |
| Praise | Positive feedback that names nothing specific. Praise for something specific (ease of use, speed, security) goes in that aspect's category with positive sentiment | "Great 👍" |
| Other | Doesn't fit any category above | — |

Themes (the short pain-point phrase) are free text, so new problems can
still surface even if the category is "Other". A high share of "Other" is
the signal to revise the taxonomy.

**Changing the list:** the Product Owner can change the categories without
rebuilding the software (FR-16), so the same platform can be pointed at
another product, another bank or a non-banking use case.

---

## 3. User / Persona

**Primary user: Product Manager** (see product brief §2).

> *Priya, Product Manager for the Santander mobile banking app.* Between
> one hundred and eight hundred Google Play reviews land each month. In some
> months most are complaints; in others the real complaints are buried among
> five-star one-liners. She wants to know which problems are growing,
> whether the latest release caused them, and have quotes ready to make the
> case to engineering — without reading thousands of reviews first.

Secondary users (Head of Product, Product Ops, Customer Support leads) can
use the same dashboard but no features are built specifically for them in
the MVP.

---

## 4. User Journey

1. **Upload** a CSV of feedback, or use the sample data.
2. **Check the file:** see straight away whether it was accepted, and how many
   rows were skipped and why.
3. **Wait for the analysis:** a progress bar shows how far it has got. The
   full 2,618-review dataset takes about 6 minutes.
4. **Read the answer first:** the biggest problem in one sentence, then the
   ranked pain points.
5. **Check the evidence:** open a pain point to read the real customer quotes
   behind it.
6. **Explore:** filter by category, sentiment, date or app version, and look
   at trends over time.
7. **Hand off:** download the Action summary for Engineering, Product and
   Operations, or export every review with its labels.

The processing steps behind this journey are in the
[architecture document, §1](ai-customer-intelligence-platform-03-ai-architecture-and-decision-log.md#1-system-architecture).

---

## 5. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| **FR-01 Upload feedback** | The user shall be able to upload a CSV file containing customer feedback. | Must |
| **FR-02 Validate file** | The system shall check required columns exist, reject files over 5,000 rows / 5 MB, and report how many rows were skipped (e.g. empty feedback) and why. | Must |
| **FR-03 Redact personal data** | The system shall remove email addresses, phone numbers and card/account-number patterns from feedback text before it is sent to the AI service. | Must |
| **FR-04 Classify feedback** | The system shall assign each feedback item one **main** category from the controlled taxonomy (§2.5), chosen by **outcome**: the task the customer was trying to do that went wrong. The cause goes in the secondary categories. *(Changed v0.5, CR-08; was "the issue given most words or anger".)* | Must |
| **FR-04b Secondary issues** | Where a review raises other distinct issues, the system shall record up to 3 secondary categories from the same taxonomy. | Must |
| **FR-05 Sentiment** | The system shall label each item positive, negative, neutral or mixed. | Must |
| **FR-06 Theme extraction** | The system shall produce a short (≤ 8 word) theme describing the main point of each item. | Must |
| **FR-07 Problem interpretation** | For negative or mixed items, the system shall state the underlying customer problem in one sentence. | Should |
| **FR-08 Aggregate** | The system shall count items and calculate percentages by category, sentiment, theme and segment. | Must |
| **FR-09 Rank pain points** | The system shall rank the top 10 pain points by number of negative/mixed mentions — counting main **and** secondary issues — showing count, % of total and how often it was the main issue. | Must |
| **FR-10 Supporting evidence** | For every pain point shown, the system shall display at least 3 verbatim quotes from the uploaded file (or all, if fewer than 3 exist). | Must |
| **FR-11 Filters** | The user shall be able to filter results by category, sentiment, date range and segment (app version). | Should |
| **FR-12 Charts** | The dashboard shall show category volume, sentiment split, and pain-point counts as charts. | Must |
| **FR-13 Opportunity suggestions** | The system shall suggest up to 5 product opportunities based on the top pain points, each linked to the pain point it addresses and clearly labelled "AI suggestion". | Could |
| **FR-14 Export** | The user shall be able to download a CSV of every item with its category, sentiment, theme and problem. | Must |
| **FR-15 Processing status** | The system shall show progress while analysis runs and a summary when it completes (items analysed, items failed). | Should |
| **FR-16 Configurable taxonomy** | The Product Owner shall be able to change the categories and their definitions without changing the software. | Must |
| **FR-17 Action summary** | The dashboard shall group the ranked pain points by suggested owner team (Engineering, Product, Operations), with example themes, related issues, app versions, trend and a quote, downloadable as Markdown. *(Added v0.5, CR-17: outside the original scope.)* | Could |

---

## 6. AI Quality Requirements

What the client needs from the AI, and how it will be judged. How each one
is met technically is in the [architecture document, §2.4](ai-customer-intelligence-platform-03-ai-architecture-and-decision-log.md#24-how-the-ai-requirements-are-met).

| Area | Requirement |
|---|---|
| **Accuracy** | At least 85% agreement with human labels on category and on sentiment, using a human-labelled set of 50 reviews, **measured separately on low-star reviews**, before users see it. |
| **Every issue counts** | When a review raises several issues, each one counts in the pain-point ranking, while the review keeps one main issue as its headline. |
| **Consistency** | The same review always gets the same labels. Checked in the evaluation with duplicate reviews. |
| **Real evidence only** | Every insight traces back to real reviews. Quotes are always the customer's own words, never written by the AI. |
| **Nothing lost silently** | A review the AI could not label is shown as "Unclassified" and counted. It is never dropped or guessed. |
| **Uncertainty shown** | Labels the AI was less sure about are counted and flagged so a person can check them. *(Threshold to tune against the evaluation set.)* |
| **Short reviews** | One- or two-word reviews ("good", "rubbish") are still labelled, but aren't expected to produce a useful theme. |
| **AI suggestions labelled** | Opportunity suggestions are marked "AI suggestion" and linked to the pain points they come from. |
| **Speed** | 1,000 reviews analysed in under 3 minutes; the full 2,618-review dataset in under 8 minutes. |
| **File size** | Up to 5,000 rows or 5 MB per upload, enough for the nine-month working dataset with room to spare. |
| **Cost** | Under £1 per 1,000 reviews analysed. Charts, filters and exports cost nothing extra. |

---

## 7. Non-Functional Requirements

| Area | Requirement |
|---|---|
| **Performance** | Dashboard filters and charts respond in under 1 second once analysis is complete. |
| **Security** | Access keys for the AI service are stored securely, never in the code or the repository. The app is served over HTTPS. |
| **Privacy** | Personal data removed before reviews are sent to the AI service (FR-03). Uploaded files are not used to train models and are deleted after the session / 24 hours. Reviewer names are not present in the dataset and must not be added. *(Met from v0.5: saved results are deleted after 24 hours, CR-18. See Appendix A.3.)* |
| **Scalability** | Not a goal for the MVP. Batching design allows larger files later without redesign. |
| **Reliability** | A problem with the AI service affects only some reviews, never the whole upload. Results are kept once analysed, so refreshing the page doesn't re-run (and re-pay for) the analysis. |
| **Usability** | A first-time user can upload a file and reach the top pain points without instructions. |
| **Transparency** | The dashboard states that categories, sentiment and suggestions are AI-generated, and shows how many items were unclassified or low-confidence. |

---

## 8. Data Sourcing & Ethics

- **Origin:** public Google Play reviews, collected by a third party and
  published on Hugging Face. The dataset card states no licence, so it is
  used for non-commercial portfolio purposes only.
- **Personal data:** the dataset contains no reviewer names or IDs. Review
  text is still redacted for emails, phone numbers and account numbers
  before any review is sent to the AI service.
- **Repository:** only the small working slice and the evaluation set are
  committed to GitHub, not the full 700k-row file. The README links to the
  original source so the work is reproducible.
- **Known data issues:** 9,885 rows have a negative `time_to_reply(h)`
  (impossible values); 70 rows have no review text. Neither field is used
  by the MVP, and empty reviews are rejected at validation (FR-02).
- **Bias:** reviews are self-selected — very happy and very unhappy
  customers write more. Insights describe *reviewers*, not all customers.

---

## 9. Out of Scope (MVP)

- Live integrations with Google Play, App Store, helpdesk or survey tools (CSV only)
- User accounts, logins, teams or permissions
- Saving and comparing analyses over time / trend alerts
- Competitor comparison across banks *(dataset supports it — strong v2 candidate)*
- Analysing the bank's replies to reviews
- Editing categories inside the app (the Product Owner changes them outside the app, FR-16)
- More than 3 secondary issues per review
- Languages other than English
- Automatic roadmap or ticket creation (e.g. pushing to Jira)
- Fine-tuning or training a custom model
- AI making prioritisation decisions — it informs, the PM decides

Anything later added from this list, or beyond it, is recorded in
[Appendix A](#appendix-a--changes-since-baseline) with its change record.

---

## 10. Open Questions

| Question | Owner | Status |
|---|---|---|
| Which AI model and hosting? | Delivery Lead | **Resolved:** Claude Haiku, hosted on Streamlit Community Cloud ([doc 03](ai-customer-intelligence-platform-03-ai-architecture-and-decision-log.md), D8 and D15). Approval of the AI provider by Information Security is still open ([Brief](ai-customer-intelligence-platform-01-product-business-brief.md), A5) |
| What caused the July 2025 jump in volume and ratings? | Product Owner | **Open:** check app version history and in-app rating prompts |
| Does the 12-category taxonomy keep "Other" under ~10%? | Product Owner | **Resolved:** 1.9% "Other" across all 2,618 reviews |
| Should Praise be split to give positive insight too? | Product Owner | **Resolved (v0.4):** specific praise is labelled by the aspect praised |

---

## 11. Expected Business Outcomes

The client will judge the MVP on these outcomes, taken from the
[Brief, §6](ai-customer-intelligence-platform-01-product-business-brief.md#6-business-value--success-metrics). The accuracy targets are in §6 above.

| Outcome | Target | How it will be measured | Owner |
|---|---|---|---|
| Less time spent on analysis | From ~12 hours to under 2 hours per PM per monthly review *(assumption A1)* | Pilot PMs log time for one review cycle before and after | Product Owner |
| Every review analysed | From a sample to 100% | Rows analysed ÷ rows received, shown on every run | Product Owner |
| Problems seen sooner | Same day as upload, instead of the monthly review | Time from export to a ranked view | Business Users |
| Used to make decisions | Used in the next 2 prioritisation cycles by the pilot PMs | Pilot PMs report whether the output changed or confirmed a priority | Project Sponsor |

Results against these outcomes are reported in the [product case study](ai-customer-intelligence-platform-09-product-case-study.md).

---

## 12. Approvals

Roles are defined in the [Brief, §8](ai-customer-intelligence-platform-01-product-business-brief.md#8-stakeholders-and-decision-rights). Client roles are titles only.

| What is approved | By | Status |
|---|---|---|
| Requirements (this document) | Product Owner | Pending: shared with the mentor for review (milestone M1) |
| Scope, budget and timeline | Project Sponsor | Pending |
| Privacy requirement and use of an external AI provider | Information Security / DPO | Pending |

---

## Appendix A — Changes since baseline

The requirements were baselined at **v0.4 (30 Oct 2026)**, when they were
shared with the mentor for review (milestone M1, still in review). Every change since then has a change
record in the [change control log](ai-customer-intelligence-platform-10-change-control-log.md).
Changes made while drafting (v0.2 to v0.4) are listed too, so the whole
history of scope is in one place.

**Scope column:** *In scope* means the change refines or delivers something
the BRD already asked for. *Added* means the BRD did not ask for it. *No BRD
impact* means a delivery, repository or defect change with no effect on
requirements.

### A.1 Change register (BRD view)

| CR | Date | Change | Scope | Effect on this BRD | BRD version |
|---|---|---|---|---|---|
| CR-01 | 30 Oct | Working dataset widened from Aug 2025 to Jan–Sep 2025 (2,618 reviews) | In scope (data) | §2.1 dataset, §2.2 baseline recomputed | v0.3 |
| CR-02 | 30 Oct | Upload limit raised from 2,000 to 5,000 rows | In scope | FR-02, AI requirements (max file size) | v0.3 |
| CR-03 | 30 Oct | Main category plus up to 3 secondary categories | **Added** | New FR-04b; FR-09 counts secondary issues; results include secondary issues | v0.4 |
| CR-04 | 30 Oct | Taxonomy v2: Praise narrowed, crash and "old app better" rules | In scope | §2.5 taxonomy | v0.4 |
| CR-05 | 31 Oct | Fix for a change in the AI provider's software | No BRD impact | None (defect) | — |
| CR-06 | 31 Oct | "Temperature 0" replaced by repeatability measured in the eval | In scope | AI requirements (model behaviour) | v0.4 text updated |
| CR-07 | 31 Oct | Commit author rewritten for privacy | No BRD impact | None (repository) | — |
| CR-08 | 31 Oct | Main issue chosen by **outcome** (prompt and taxonomy v3) | In scope (changes a rule) | **FR-04 rule changed**; §2.5 taxonomy v3 | v0.5 |
| CR-09 | 31 Oct | 6 evaluation labels changed to the outcome rule | In scope | None to requirements; affects how the quality bar is measured (bias risk R07) | — |
| CR-12 | 31 Oct | Batches sent in parallel | In scope | Delivers the response-time target (8 min → 6.1 min achieved) | — |
| CR-13 | 31 Oct | UAT dashboard fixes (filters drive the summary, readable charts) | In scope | Delivers FR-11, FR-12 and the transparency NFR | — |
| CR-14 | 31 Oct | Sample results shipped with the code; versions pinned | **Added** (small) | Not in the BRD: a demo that loads instantly at no cost. Supports the reliability NFR | — |
| CR-15 | 1 Nov | Deployed to Streamlit Community Cloud, two weeks early | No BRD impact (schedule) | Security NFR met (key in Streamlit Secrets, HTTPS) | — |
| CR-16 | 1 Nov | Plain-English signposting: answer-first headline, definitions, tooltips | In scope | Delivers the usability and transparency NFRs | — |
| CR-17 | 1 Nov | Action summary page for Engineering, Product and Operations | **Added** | **New FR-17** (Could). Stays inside §9: it downloads a summary but does not create tickets automatically | v0.5 |
| CR-18 | 1 Nov | Saved results deleted after 24 hours | In scope (fixes a gap) | Delivers the privacy NFR, which was not met (A.3) | v0.5 |
| CR-19 | 5 Nov | Client-focused documents after mentor review | No requirement change | Technical detail moved to doc 03; §2.4, §4 and §6 rewritten in business terms; §11 outcomes and §12 approvals added | v0.6 |

Proposed but not decided: CR-10 (taxonomy boundaries) and CR-11 (outcome rule
and praise). Neither changes a requirement; both aim to raise accuracy.

### A.2 Summary: what was added beyond the original scope

| Added | Why it was worth it | Cost or risk |
|---|---|---|
| Secondary categories (CR-03) | 20 of 50 labelled reviews raised several issues; one label per review hid real complaints from the ranking | More complex schema and eval; extra accuracy measures |
| Shipped sample results (CR-14) | Live demo loads in about 1 second at no AI cost, even after a cloud restart | One results file to regenerate whenever the prompt or model changes |
| Action summary page (CR-17) | Turns the ranking into a hand-off for Engineering, Product and Operations | Which team owns which issue is a judgement the client can change; trends need care because review volume jumped in July 2025 |

### A.3 Deviations from this BRD

| Requirement | What the BRD says | What the app does | Action |
|---|---|---|---|
| Privacy NFR | Uploaded files are deleted after the session / 24 hours | Analysed results, including the original review text, were stored (decision D14) and nothing deleted them. On the cloud they lasted until the app restarted; locally until the file was deleted | **Fixed by CR-18 (1 Nov):** saved results older than 24 hours are deleted whenever the page loads or an analysis starts, and the deleted text is overwritten on disk. The sample data still loads instantly at no cost. The app tells users this. **No open deviations remain.** |

### A.4 Planned scope not yet approved

The programme's Week 2 asks for **saved past analyses** and **user login**.
Both are listed as out of scope in §9 today. Each needs a change record before
work starts. Saved past analyses would also need the 24-hour rule (CR-18) revisited, and login would help with controlling API cost.
