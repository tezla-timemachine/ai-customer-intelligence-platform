# Business Requirements Document — AI Customer Intelligence Platform (MVP)

> **Status:** Draft v0.4 · Covers challenge Parts 2 (MVP definition) and 3 (BRD).
> Builds on [Product / Business Brief](ai-customer-intelligence-platform-01-product-business-brief.md). Figures marked *(assumption)*
> are placeholders to validate during build and evaluation.
>
> **v0.2:** grounded in a real dataset — UK banking app reviews — with a
> banking-specific taxonomy and a measured baseline from an existing topic model.
> **v0.3:** working dataset widened from one month (Aug 2025, 837 reviews) to
> Jan–Sep 2025 (2,618 reviews) after finding August was unrepresentative.
> **v0.4:** after labelling the evaluation set — reviews with several issues now get a main
> category plus up to 3 secondary categories; Praise narrowed to non-specific praise.

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

| Capability | Done by | Why |
|---|---|---|
| Classify each item into a product-issue category | **LLM** | Customers describe the same problem in many ways; rules miss paraphrases |
| Detect sentiment (positive / negative / neutral / mixed) | **LLM** | Mixed feedback and sarcasm need language understanding |
| Extract a short theme / pain point per item | **LLM** | Turning "it just sits doing nothing" into "login hangs after security code" is interpretation |
| Interpret the underlying customer problem | **LLM** | Same reason — meaning, not keywords |
| Suggest possible product opportunities from top pain points | **LLM** (labelled as suggestions) | Generative task; useful prompt for the PM, not a decision |
| Validate the file (columns, empty rows, size) | **Code** | Must be exact and predictable |
| Remove obvious personal data (emails, phone numbers, account/card numbers) before sending to the LLM | **Code** | Pattern matching is reliable and auditable |
| Count items per category / theme | **Code** | Counting must be exactly right every time — LLMs can miscount |
| Calculate percentages and statistics | **Code** | Arithmetic is free, instant and guaranteed in code |
| Rank pain points (frequency × negativity) | **Code** | Ranking rule must be transparent and repeatable |
| Filter by category, sentiment, date, segment | **Code** | Standard data operation |
| Draw charts | **Code** | Standard charting library |
| Pick supporting quotes for each theme | **Code** selects from LLM-tagged items | Quotes are always real rows from the file, never generated text |
| Compare results with the existing topic model | **Code** | Side-by-side counts; no AI needed |
| Export results to CSV | **Code** | Standard |

**Rule of thumb used throughout:** the LLM only *reads and labels* text.
Anything that produces a number, an order or a chart is deterministic code.
This keeps the numbers trustworthy, keeps cost down (the LLM is called once
per batch of reviews, not for every chart or filter), and means the same
upload always gives the same counts.

### 2.5 Category taxonomy (controlled list)

The LLM must choose from this fixed list — it may not invent categories.
Built from reading the 2025 Santander reviews.

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

**Design decision — taxonomy as configuration:** the category list lives in
a separate config file, not in the code. Pointing the platform at a
different domain (another bank, a different product, or a non-banking use
case) means swapping the config and the data — not rebuilding.

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

## 4. User Flow

```
Upload CSV
  → Validate file            (code: columns, size, empty rows)
  → Clean & redact           (code: strip personal data)
  → Analyse feedback         (LLM: category, sentiment, theme, problem — in batches)
  → Check structured output  (code: valid JSON, allowed values; retry or flag)
  → Aggregate results        (code: counts, %, ranking)
  → Display insights         (dashboard: top pain points, charts, filters)
  → Review evidence          (click a theme → see the real quotes)
  → Export results           (CSV of every item with its labels)
```

---

## 5. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| **FR-01 Upload feedback** | The user shall be able to upload a CSV file containing customer feedback. | Must |
| **FR-02 Validate file** | The system shall check required columns exist, reject files over 5,000 rows / 5 MB, and report how many rows were skipped (e.g. empty feedback) and why. | Must |
| **FR-03 Redact personal data** | The system shall remove email addresses, phone numbers and card/account-number patterns from feedback text before it is sent to the LLM. | Must |
| **FR-04 Classify feedback** | The system shall assign each feedback item one **main** category from the controlled taxonomy (§2.5) — the issue given most words or anger. | Must |
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
| **FR-16 Configurable taxonomy** | Categories and their definitions shall be loaded from a config file, so they can be changed without code changes. | Must |

---

## 6. AI Requirements

| Area | Requirement |
|---|---|
| **Structured output** | The LLM shall return JSON only, one object per item: `{ "id", "category", "other_categories", "sentiment", "theme", "problem", "confidence" }`. `category` and `sentiment` must be values from the allowed lists. |
| **Model behaviour** | Repeatable labels: lowest randomness the provider allows (the current Anthropic SDK offers no temperature setting), verified by the evaluation's duplicate-consistency check. The prompt includes the taxonomy with definitions and 1 example per category. The model labels only what the customer said — no guessing intent beyond the text. |
| **Multiple issues in one item** | The model returns the *main* category plus up to 3 `other_categories`. Secondary categories must be from the taxonomy, distinct, and never repeat the main one — code enforces this. Every issue a customer raises counts towards the pain-point ranking. |
| **Very short reviews** | One- or two-word reviews ("good", "rubbish") are still classified (usually Praise, Other, or the aspect named — e.g. "slow" → Performance) but are not expected to produce a meaningful theme. |
| **Grounding / evidence** | Every insight shown must trace back to real rows. Quotes are pulled from the original file by row ID, never written by the LLM. Opportunity suggestions must reference the pain point(s) they come from. |
| **Failure handling** | Invalid JSON or a value outside the allowed lists → retry once; if it fails again, mark the item "Unclassified" and count it in the summary. The analysis never silently drops rows. |
| **Low confidence** | Items with `confidence` below 0.6 are flagged for optional human review. *(assumption — threshold to tune against the eval set)* |
| **Response time** | 1,000 reviews analysed in under 3 minutes; the full 2,618-review dataset in under 8 minutes *(assumption)*. Achieved by sending items in batches (~20 per call) rather than one call per row. |
| **Max file size** | 5,000 rows / 5 MB per upload for the MVP. Covers the full nine-month working dataset (2,618 rows) with headroom. |
| **Cost** | Target under £1 per 1,000 reviews *(assumption — confirm once model chosen in Part 4)*. Charts, filters and exports cost nothing because they don't call the LLM. |
| **Quality bar** | ≥ 85% category accuracy and ≥ 85% sentiment accuracy against the human-labelled evaluation set (Part 9), **measured separately on low-star reviews**, before the MVP is shown to users. |

---

## 7. Non-Functional Requirements

| Area | Requirement |
|---|---|
| **Performance** | Dashboard filters and charts respond in under 1 second once analysis is complete. |
| **Security** | API keys stored as environment variables, never in code or the repo. App served over HTTPS. |
| **Privacy** | Personal data redacted before LLM calls (FR-03). Uploaded files are not used to train models and are deleted after the session / 24 hours. Reviewer names are not present in the dataset and must not be added. |
| **Scalability** | Not a goal for the MVP. Batching design allows larger files later without redesign. |
| **Reliability** | A failed LLM call affects only its batch, not the whole upload. Results are saved once analysed so a page refresh doesn't re-run (and re-pay for) the analysis. |
| **Usability** | A first-time user can upload a file and reach the top pain points without instructions. |
| **Transparency** | The dashboard states that categories, sentiment and suggestions are AI-generated, and shows how many items were unclassified or low-confidence. |

---

## 8. Data Sourcing & Ethics

- **Origin:** public Google Play reviews, collected by a third party and
  published on Hugging Face. The dataset card states no licence, so it is
  used for non-commercial portfolio purposes only.
- **Personal data:** the dataset contains no reviewer names or IDs. Review
  text is still redacted for emails, phone numbers and account numbers
  before any LLM call.
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
- Editing categories in the app (config file only)
- More than 3 secondary issues per review
- Languages other than English
- Automatic roadmap or ticket creation (e.g. pushing to Jira)
- Fine-tuning or training a custom model
- AI making prioritisation decisions — it informs, the PM decides

---

## 10. Open Questions

- Which LLM and hosting? → decided in Part 4 (architecture & decision log).
- What caused the July 2025 jump in volume and ratings? → check app version history / in-app rating prompts.
- Does the 12-category taxonomy keep "Other" under ~10%? → check with the eval set.
- ~~Should Praise be split to give positive insight too?~~ → **Resolved (v0.4):** specific praise is labelled by the aspect praised, so the dashboard can also show what customers like.
