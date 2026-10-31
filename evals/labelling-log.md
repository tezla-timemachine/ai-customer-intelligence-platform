# Labelling Log

A record of how the evaluation set was labelled, and what changed. Everything up
to 30 Oct happened **before** any AI output was seen. Changes made **after** an AI
run are listed separately at the end, with the reason (bias control, risk R07).

| Date | Step | Outcome |
|---|---|---|
| 30 Oct 2026 | First pass: 50 reviews hand-labelled (main category + sentiment) | All 50 labelled |
| 30 Oct 2026 | Review against the category definitions | Found 2 systematic ambiguities (below) |
| 30 Oct 2026 | Taxonomy v2 + labels updated | 11 main categories changed, 20 reviews given secondary issues |
| 31 Oct 2026 | First AI run (prompt v2, claude-haiku-5-5) | Category 80%, sentiment 94%. 7 of 10 category misses were main-vs-secondary swaps |
| 31 Oct 2026 | **Post-eval:** main-issue rule changed to *outcome* (decision D17), taxonomy v3 | 6 main categories changed (below) |

## What labelling revealed

1. **Praise was ambiguous.** The v1 definition ("positive feedback with no
   problem raised") clashed with a natural instinct to label praise by
   *what* was praised. "Easy to use" was labelled Design & Usability, but
   "easy peasy" was labelled Praise. **Decision:** specific praise goes to the
   aspect praised, and Praise is kept for praise that names nothing ("Great 👍",
   "🥰"). The dashboard can now show what customers *like*, not just what
   they dislike.
2. **Many reviews raise several issues.** 20 of 50 reviews (40%) raised more
   than one distinct issue. Under single-label classification, those
   secondary complaints would never reach the pain-point ranking.
   **Decision:** main category + up to 3 secondary categories (decision D7,
   revised).
3. **Smaller definition fixes:** crashes belong to App Updates & Stability
   (Performance means slowness only), and "old app was better" with no detail
   goes to Design & Usability.

## Main-category changes

| Review | Was | Now | Why |
|---|---|---|---|
| E03, E29, E31 | Praise | Design & Usability | Praise for ease of use (rule 1) |
| E26 | Other | Praise | Non-specific praise (🥰) |
| E08, E25 | Performance | App Updates & Stability | Crashing (rule 3) |
| E14, E21 | Customer Support | App Updates & Stability | Main complaint is the app not opening; support moved to secondary |
| E22 | Identity & Security Checks | Login & Access | Most words are about the login loop |
| E32, E33 | App Updates & Stability | Design & Usability | "Old app better", no detail (rule 3) |

E34 kept as App Updates & Stability because the review mentions the update
explicitly.

## Post-eval changes: outcome rule (31 Oct 2026)

**Made after seeing AI output.** These are not corrections of individual
mistakes. The first run showed that the labels mixed two rules for choosing the
main issue: sometimes the *outcome* (what the customer couldn't do), sometimes
the *cause* (what broke). Tez chose one rule, **outcome** (decision D17), and it
was applied to all 50 labels. Six broke it. In each case the old main issue
became a secondary issue, so no issue was dropped.

| Review | Customer said (short) | Was | Now | Old main moved to secondary |
|---|---|---|---|---|
| E13 | Won't text a verification code, so I cannot log on | Identity & Security Checks | Login & Access | Yes |
| E14 | App keeps stopping and not letting me log in | App Updates & Stability | Login & Access | Yes |
| E24 | No more fingerprint login, code every time | Missing Feature | Login & Access | Yes |
| E41 | Layout changed, button to make payments missing | Missing Feature | Payments & Transfers | Yes |
| E44 | Can't log in with biometrics, can't change settings, can't pay card bill | Identity & Security Checks | Login & Access | Yes |
| E47 | Can't change my card PIN in the app | Missing Feature | Cards | Yes |

**Check against bending labels towards the AI:** compared with the prompt v2
run, 4 of these changes agree with the AI's answer (E14, E24, E44, E47) and
2 now disagree with it (E13, E41). The rule was applied wherever it fell.
