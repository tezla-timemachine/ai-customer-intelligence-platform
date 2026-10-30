# Evaluation Set — Labelling Guide

The evaluation set is the **source of truth** for AI accuracy. The AI is only
as trustworthy as these labels, so they are written by a human, by hand,
**before** looking at any AI output (risk R07).

## The set

- **50 real Santander app reviews from 2024**, deliberately chosen to cover
  the case types in the challenge brief.
- Taken from **2024, not the Jan–Sep 2025 working data**, so the AI is
  tested on reviews it was never tuned on.

| Case type | n | What it tests |
|---|---|---|
| Positive | 5 | Praise is recognised, including praise that mentions fees or branches |
| Negative – single issue | 9 | Each main category is recognised |
| Mixed sentiment | 6 | Praise and complaint together → *mixed*, not forced to one side |
| Multiple problems | 5 | The *main* issue is picked from several |
| Very short | 6 | "slow", "🥰", "easy peasy" |
| Ambiguous | 5 | "Not as good as the previous app"; a 5★ rating on a complaint |
| Duplicate | 3 | Identical text gets an identical label |
| Sarcasm | 5 | "Now I can't even log on. Great" → negative |
| Feature request | 3 | Missing Feature vs a complaint |
| Unrelated to the app | 3 | Savings rates, branch closures, gibberish → *Other* |

## How to label

Open `eval_set.xlsx` (Excel, Numbers or Google Sheets). Fill in the **yellow columns**.
To save typing, use the **number** for a category (1–12) and the **letter** for a sentiment
(P positive · N negative · U neutral · M mixed). Both are listed in the *categories* sheet.
Full names work too.

1. **expected_category:** the one category for the review's **main** issue.
   Definitions are in the *categories* sheet. Judge only what the customer
   wrote, not what they might have meant.
2. **expected_sentiment:**
   - *positive:* only praise
   - *negative:* only complaint (**sarcastic praise counts as negative**)
   - *neutral:* factual, no clear feeling
   - *mixed:* genuine praise **and** a genuine complaint
3. **expected_other_categories (optional):** if the review raises **other distinct
   issues** besides the main one, list them (numbers or names, comma separated,
   e.g. `4, 1`). Leave blank if there is only one issue. Only list an issue
   the customer actually raises, not a word that just appears.
4. **label_notes:** optional. Use it when a call was hard ("could be Login or
   Security Checks; chose Security because the selfie step is the blocker").
   These notes become examples in your case study.

## Rules for hard calls (decide once, apply every time)

| Situation | Rule |
|---|---|
| Several issues | **Main** = the one given most words or anger (if equal, the first mentioned). List the rest in expected_other_categories. |
| Praise for something specific ("easy to use", "fast", "feels secure") | That aspect's category, sentiment positive |
| Praise that names nothing ("Great 👍", "🥰") | Praise, positive |
| Crashes / won't open | App Updates & Stability (Performance is only for slowness) |
| "Old app was better" with no detail | Design & Usability, negative |
| Login fails *because* of an ID/selfie/OTP step | Identity & Security Checks |
| Login fails for any other reason | Login & Access |
| A button or feature removed in an update | Missing Feature if they ask for it back; Design & Usability if it's about layout |
| Star rating contradicts the text | Label the **text**, and add a note |
| Positive review about something that isn't the app (branch staff, fees) | Praise if it's positive overall; Other if it isn't about the app or bank service at all |

## Bias checks (risk R07)

- **Label everything before running `run_eval.py`.** Don't change a label
  after seeing the AI's answer unless you find a genuine mistake. If you do,
  record it in `label_notes` ("changed after eval run: …").
- **Self-agreement:** a few days later, re-label 10 random rows without
  looking at your first answers. Below 85% agreement means the guide needs
  clearer rules.
- If possible, ask your mentor to label 10 rows too, and compare.

## Running the evaluation

```bash
LLM_PROVIDER=anthropic ANTHROPIC_API_KEY=... python evals/run_eval.py
```

Results are written to `evals/results/`: a CSV comparing expected and AI
output for every row, and a markdown summary with accuracy by case type,
the most common confusions, every failure, and a section for you to write
up the **failure patterns**.
