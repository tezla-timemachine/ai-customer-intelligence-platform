# Labelling Log

A record of how the evaluation set was labelled, and what changed. All of it
happened **before** any AI output was seen.

| Date | Step | Outcome |
|---|---|---|
| 30 Oct 2026 | First pass: 50 reviews hand-labelled (main category + sentiment) | All 50 labelled |
| 30 Oct 2026 | Review against the category definitions | Found 2 systematic ambiguities (below) |
| 30 Oct 2026 | Taxonomy v2 + labels updated | 11 main categories changed, 20 reviews given secondary issues |

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
