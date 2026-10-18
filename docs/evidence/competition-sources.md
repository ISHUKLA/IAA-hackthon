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
