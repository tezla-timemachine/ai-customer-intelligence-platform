# Evaluation run — 20261031-1318_anthropic-claude-haiku-5-5

- Model: `anthropic / claude-haiku-5-5` · prompt `classify_v2`
- Examples: 50 · unclassified: 0 · retries: 0 · time: 44.3s
- **Quality gate (≥85% category and sentiment): FAIL ❌**

| Measure | Accuracy |
|---|---|
| Category | 80.0% |
| Sentiment | 94.0% |
| Both correct | 74.0% |
| Category — low-star reviews only (n=31) | 74.2% |
| Sentiment — low-star reviews only | 93.5% |
| Duplicates labelled consistently | Yes |
| AI main category is one of the issues you listed (lenient) | 94.0% |
| Secondary issues found (recall, n=26) | 84.6% |
| Secondary issues flagged that were right (precision, n=26) | 80.8% |

## By case type

| case_type               |   n |   category |   sentiment |
|:------------------------|----:|-----------:|------------:|
| ambiguous               |   5 |       60   |       100   |
| duplicate               |   3 |      100   |       100   |
| feature request         |   3 |       66.7 |       100   |
| mixed sentiment         |   6 |       66.7 |        83.3 |
| multiple problems       |   5 |       80   |       100   |
| negative – single issue |   9 |       66.7 |       100   |
| positive                |   5 |      100   |       100   |
| sarcasm                 |   5 |       80   |       100   |
| unrelated to the app    |   3 |      100   |        33.3 |
| very short              |   6 |      100   |       100   |

## Most common category confusions (expected → AI)

| expected_category          | ai_category             |   count |
|:---------------------------|:------------------------|--------:|
| App Updates & Stability    | Design & Usability      |       1 |
| App Updates & Stability    | Login & Access          |       1 |
| App Updates & Stability    | Performance             |       1 |
| Identity & Security Checks | Login & Access          |       1 |
| Login & Access             | App Updates & Stability |       1 |
| Login & Access             | Performance             |       1 |
| Missing Feature            | Cards                   |       1 |
| Missing Feature            | Login & Access          |       1 |
| Payments & Transfers       | Design & Usability      |       1 |
| Payments & Transfers       | Missing Feature         |       1 |

## Sentiment confusions (expected → AI)

| expected_sentiment   | ai_sentiment   |   count |
|:---------------------|:---------------|--------:|
| negative             | neutral        |       2 |
| mixed                | neutral        |       1 |

## Every failure

- **E10** (negative – single issue, 1★) “Stop changing the app layout!! My pay and transfer button is gone and now I cannot send money!” — expected *Payments & Transfers / negative* (+ Design & Usability), AI *Design & Usability / negative* (+ Payments & Transfers)
- **E11** (negative – single issue, 1★) “Why can't I pay off my card using the app? It's pretty useless if you ask me!” — expected *Payments & Transfers / negative* (+ Missing Feature), AI *Missing Feature / negative* (+ Payments & Transfers)
- **E14** (negative – single issue, 1★) “Hi I have been trying to login to my account but unfortunately the app is keep stopping and not letting me login I have called the customer service and told the” — expected *App Updates & Stability / negative* (+ Login & Access; Customer Support), AI *Login & Access / negative* (+ App Updates & Stability; Customer Support)
- **E16** (mixed sentiment, 3★) “I find it slower to log on than the old but very clear once on” — expected *Login & Access / mixed* (+ Performance), AI *Performance / mixed* (+ Design & Usability)
- **E19** (mixed sentiment, 3★) “It's ok. Hoping for better transaction searching and a way to quickly view account balance. I used to use the widget but that appears to have gone.” — expected *Missing Feature / mixed* (+ Design & Usability), AI *Missing Feature / neutral*
- **E20** (mixed sentiment, 2★) “Problems loading and connecting most of the time. When it works though, the system is fine.” — expected *App Updates & Stability / mixed*, AI *Performance / mixed*
- **E24** (multiple problems, 1★) “No more finger print login, have to put my code in each time I login. No quick ballance, the whole app feels clunky compared to 1 year ago when it was a good ap” — expected *Missing Feature / negative* (+ Login & Access; Design & Usability), AI *Login & Access / negative* (+ Missing Feature; Design & Usability)
- **E34** (ambiguous, 3★) “don't like this last update. preferred the other” — expected *App Updates & Stability / negative*, AI *Design & Usability / negative*
- **E36** (ambiguous, 5★) “App is having issues as per today... can't get in. Please provide an update. Thanks” — expected *Login & Access / negative*, AI *App Updates & Stability / negative* (+ Login & Access)
- **E44** (sarcasm, 1★) “Total unnecessary downgrade. Unable to login via biometrics anymore, no option to change security settings, and now won't let me pay credit card bill directly. ” — expected *Identity & Security Checks / negative* (+ Login & Access; Payments & Transfers), AI *Login & Access / negative* (+ Missing Feature; Payments & Transfers)
- **E47** (feature request, 4★) “App is very useful but one thing missing is the ability to change my pin on my cards. I'm disabled so can't always get to a branch ATM to change it if i need to” — expected *Missing Feature / mixed* (+ Cards), AI *Cards / mixed* (+ Missing Feature)
- **E49** (unrelated to the app, 5★) “Obselete attack staff dead by england help” — expected *Other / negative*, AI *Other / neutral*
- **E50** (unrelated to the app, 1★) “Necessary now all the local branches are closed.” — expected *Customer Support / negative*, AI *Customer Support / neutral*

## Failure patterns (fill in after reading the failures)

1. 
2. 
3. 