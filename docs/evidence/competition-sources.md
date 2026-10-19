# Competition sources and source-status rules

Official pages read during this chat, most recently overview verified on 18 October 2026:

- Overview: https://www.kaggle.com/competitions/iaa-ai-assisted-hackathon-2026-part-1/overview
- Data: https://www.kaggle.com/competitions/iaa-ai-assisted-hackathon-2026-part-1/data
- Rules: https://www.kaggle.com/competitions/iaa-ai-assisted-hackathon-2026-part-1/rules

Exact metric excerpt: **“Tweedie D² score (power = 1.5)”**.

Official submission illustration:

```text
row_id, prediction
M02409311,583.47
B01834522,412.10
```

The actual sample names are row_id and prediction. Prose permits nonnegative predictions. Standard Tweedie implementations at power 1.5 require strictly positive predictions: separate a format check from local scoring compatibility. The output is policy-period expected ultimate cost, net of excess/recoveries and excluding declined claims; this sentence is a paraphrase.

The overview permits GLMs, ML or combinations. Judging weights are 40/25/20/15 for performance/adaptation, effective AI use, trust/guardrails and communication. Part 1's current displayed deadline was 23 October 2026, 18:00 CEST, while detailed rules contain date placeholders. Do not use an old relative countdown as a current deadline. A foundational-rule/overview discrepancy about leaderboard versus panel judging should remain an organiser-clarification item, not be silently reconciled.

Exact score pooling/weights and scorer implementation have not been established. Accessing public pages is allowed; accepting terms, entering teams, posting questions or uploading predictions is a separate action. If the harness cannot access a page, record that limitation and use this dated, previously verified extract with its provenance. Do not fabricate a fresh verification or loop around a login/bot wall.

Technical primary sources:

- D²: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.d2_tweedie_score.html
- Deviance: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_tweedie_deviance.html
- Metric mathematics: https://scikit-learn.org/stable/modules/model_evaluation.html
- Claude Code memory: https://code.claude.com/docs/en/memory

Original context.md and what-good-looks-like.md express project choices as well as facts. They are not independent proof of official rules or professional-standard requirements. Log conflicts and identify any proposed change for human review.

## Step 9 current-access check, 19 October 2026

Fresh retrieval attempts at 12:58:30 UTC failed for the competition overview, data, evaluation and rules URLs: the public-page tool reported each URL inaccessible and returned no page text. The evaluation route from the Step 1 register (`overview/evaluation`) also failed at 13:06:31 UTC. Exact URLs and results are in reports/step9/official-rules-check.json. No terms were accepted, organiser contacted or submission made.

All successful extracts above and in docs/step1/source-register.md remain dated PRIOR verification. Current deadlines, submission limits and final-entry limits are unresolved; neither the old five-per-day plan nor the later ten-per-day extract is claimed current. Scorer code, pooling and weights remain unresolved. This access limitation does not erase the established local file/row contract, but must be resolved before a separate upload decision.

## Step 10 current-access check, 19 October 2026

At 13:21:03 UTC, fresh public-page requests for overview, data, overview/evaluation and rules again returned inaccessible-URL results and no page text. Exact URLs/statuses are in reports/step10/official-rules-check.json. No current deadline, Part 1-specific deliverable timing, judging formula, daily limit or final-selection rule is invented. The older source register remains prior verification only. Step 10 treats missing current official requirements as a critical readiness blocker and does not contact organisers, accept terms or upload anything.

## Later signed-in page read, 19 October 2026

After the Step 10 access failure, a fresh in-app browser read of the [official Data page](https://www.kaggle.com/competitions/iaa-ai-assisted-hackathon-2026-part-1/data) established that paid-to-date is net of policy excess, incurred-to-date is paid plus the current case estimate, recoveries are separately described as third-party/salvage receipts, and `repudiated` is the site's term for declined. The glossary distinguishes incurred from ultimate, and the page explicitly warns that some 2024 claims were unreported at the valuation date and open claims can develop. This resolves the excess and declined-status terminology, **not** whether incurred already nets recorded recoveries or whether case estimates are adequate. The signed-in page also displayed that viewing competition files requires agreeing to rules; no terms were accepted here. This later retrieval supersedes the earlier claim that no current Data-page text could be obtained; the dated Step 9/10 failed retrievals remain historical facts.
