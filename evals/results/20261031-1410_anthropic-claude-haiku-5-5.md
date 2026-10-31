# Evaluation run — 20261031-1410_anthropic-claude-haiku-5-5

- Model: `anthropic / claude-haiku-5-5` · prompt `classify_v3`
- Examples: 50 · unclassified: 0 · retries: 0 · time: 38.4s
- **Quality gate (≥85% category and sentiment): PASS ✅**

| Measure | Accuracy |
|---|---|
| Category | 92.0% |
| Sentiment | 94.0% |
| Both correct | 86.0% |
| Category — low-star reviews only (n=31) | 93.5% |
| Sentiment — low-star reviews only | 93.5% |
| Duplicates labelled consistently | Yes |
| AI main category is one of the issues you listed (lenient) | 96.0% |
| Secondary issues found (recall, n=27) | 88.9% |
| Secondary issues flagged that were right (precision, n=31) | 77.4% |

## By case type

| case_type               |   n |   category |   sentiment |
|:------------------------|----:|-----------:|------------:|
| ambiguous               |   5 |       80   |       100   |
| duplicate               |   3 |      100   |       100   |
| feature request         |   3 |      100   |       100   |
| mixed sentiment         |   6 |       66.7 |        83.3 |
| multiple problems       |   5 |      100   |       100   |
| negative – single issue |   9 |      100   |       100   |
| positive                |   5 |       80   |       100   |
| sarcasm                 |   5 |      100   |       100   |
| unrelated to the app    |   3 |      100   |        33.3 |
| very short              |   6 |      100   |       100   |

## Most common category confusions (expected → AI)

| expected_category       | ai_category        |   count |
|:------------------------|:-------------------|--------:|
| App Updates & Stability | Design & Usability |       1 |
| App Updates & Stability | Performance        |       1 |
| Design & Usability      | Fees & Charges     |       1 |
| Design & Usability      | Login & Access     |       1 |

## Sentiment confusions (expected → AI)

| expected_sentiment   | ai_sentiment   |   count |
|:---------------------|:---------------|--------:|
| negative             | neutral        |       2 |
| mixed                | neutral        |       1 |

## Every failure

- **E02** (positive, 5★) “easy to use, don't get charged for using card in spain” — expected *Design & Usability / positive* (+ Fees & Charges), AI *Fees & Charges / positive* (+ Design & Usability)
- **E18** (mixed sentiment, 4★) “Easy to use other than Biometric checks but think that's my phone problem.” — expected *Design & Usability / mixed* (+ Login & Access), AI *Login & Access / mixed* (+ Design & Usability)
- **E19** (mixed sentiment, 3★) “It's ok. Hoping for better transaction searching and a way to quickly view account balance. I used to use the widget but that appears to have gone.” — expected *Missing Feature / mixed* (+ Design & Usability), AI *Missing Feature / neutral* (+ Design & Usability)
- **E20** (mixed sentiment, 2★) “Problems loading and connecting most of the time. When it works though, the system is fine.” — expected *App Updates & Stability / mixed*, AI *Performance / mixed*
- **E34** (ambiguous, 3★) “don't like this last update. preferred the other” — expected *App Updates & Stability / negative*, AI *Design & Usability / negative*
- **E49** (unrelated to the app, 5★) “Obselete attack staff dead by england help” — expected *Other / negative*, AI *Other / neutral*
- **E50** (unrelated to the app, 1★) “Necessary now all the local branches are closed.” — expected *Customer Support / negative*, AI *Customer Support / neutral*

## Failure patterns (fill in after reading the failures)

1. 
2. 
3. 