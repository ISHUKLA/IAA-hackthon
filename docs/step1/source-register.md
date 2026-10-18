# Step 1 source register

Status date: 18 October 2026. This register separates current organiser material, prior measured findings, user choices, project interpretations and unresolved assumptions. The Kaggle pages were freshly retrieved from their public, anonymous views on the status date; no login, invitation acceptance, rules acceptance, organiser contact or submission action was performed. Relative countdown text is deliberately not treated as a durable date.

## Source precedence and status labels

1. Current official competition pages support competition requirements, subject to conflicts within those pages.
2. Direct measurements support statements about the measured files only after their hashes are reverified.
3. The user's latest instructions and `AGENTS.md` establish scope and operating choices.
4. `context.md`, `what-good-looks-like.md` and `docs/plan.md` contain choices and interpretations, not independent proof of official rules or professional requirements.
5. A proposal in `docs/plan.md` remains proposed until a human approves it.

| Status label | Meaning |
| --- | --- |
| Official — fresh | Read from the named public Kaggle page on 18 October 2026. |
| Prior official extract | Previously verified text preserved locally; not a fresh retrieval by itself. |
| Measured — reverify | Result of an earlier file audit; applicability depends on matching the expected manifest. |
| User instruction or choice | Scope or design direction supplied by the user; not an organiser rule. |
| Project interpretation | Analytical recommendation or inference that requires evidence or approval. |
| Unresolved | The available sources do not establish the answer. |

## Register

| ID | Source URL or path | Section | Date and status | Supported claim | Limitation |
| --- | --- | --- | --- | --- | --- |
| O01 | https://www.kaggle.com/competitions/iaa-ai-assisted-hackathon-2026-part-1/overview | Description — Week 1 | 2026-10-18; Official — fresh | The developed-market data cover private motor, home buildings and home contents over policy years 2021–2024. The task is a 2025 expected-ultimate claim-cost prediction. GLMs, machine learning or combinations are allowed. | The page does not prescribe one model family, an ensemble or a target-development method. |
| O02 | https://www.kaggle.com/competitions/iaa-ai-assisted-hackathon-2026-part-1/overview/evaluation | Evaluation | 2026-10-18; Official — fresh | The four evaluation categories are Pricing Performance & Adaptation 40%, Effective Use of AI 25%, Trust, Validation & Guardrails 20%, and Communication & Documentation 15%. | The prose does not define a complete numeric formula for combining leaderboard scores with panel assessment. |
| O03 | https://www.kaggle.com/competitions/iaa-ai-assisted-hackathon-2026-part-1/overview/evaluation | Submissions and review | 2026-10-18; Official — fresh | Final deliverables after both parts include two prediction files, a video, a written report and version-controlled code. Only the first five video minutes and first five report pages are graded. AI tools may screen deliverables; final judging remains with the panel. | No page-one layout or mandatory card, SHAP, ensemble or software requirement is stated. |
| O04 | https://www.kaggle.com/competitions/iaa-ai-assisted-hackathon-2026-part-1/overview/evaluation | Submission file and Accuracy of submissions | 2026-10-18; Official — fresh | One CSV covers all three test tables; predictions must be zero or above; higher metric values are better. The target is row-level expected ultimate claim cost, not charged premium. | Exact scorer code, row/line pooling, any exposure weighting and numerical boundary handling are not published in the retrieved prose. |
| D01 | https://www.kaggle.com/competitions/iaa-ai-assisted-hackathon-2026-part-1/data | Files | 2026-10-18; Official — fresh | Training policy tables cover 2021–2024; test policy tables cover 2025; claims are reported as at 31 December 2024; files are provided in Parquet format. | Presence and content of the user's local files were not checked in Prompt 01 because `IAA_DATA_DIR` is unset. |
| D02 | https://www.kaggle.com/competitions/iaa-ai-assisted-hackathon-2026-part-1/data | How the tables link | 2026-10-18; Official — fresh | `policy_id` links claims to policies, and a claim is matched to the relevant policy row using `loss_date`; `row_id` identifies each test submission row. | The page does not settle every exceptional linkage case or define the treatment of pre-coverage audit exceptions. |
| D03 | https://www.kaggle.com/competitions/iaa-ai-assisted-hackathon-2026-part-1/data | Policy periods | 2026-10-18; Official — fresh | One policy row represents one policy for a calendar year or part-year; mid-term changes can create multiple rows, cancellations or lapses can shorten rows, and exposure is the row length in years. | Inclusive boundary handling is an explicit project instruction in `AGENTS.md`, not text established by this page excerpt. |
| R01 | https://www.kaggle.com/competitions/iaa-ai-assisted-hackathon-2026-part-1/rules | Competition-Specific Rules, 2.4 Two-Part Competition | 2026-10-18; Official — fresh | Part 1 and Part 2 private leaderboard scores are equally weighted within Pricing Performance & Adaptation; the judging panel also assesses modelling choices, adaptation, data quality and uncertainty. The other three categories are panel-assessed. | The relative weight of the private-score component and panel component inside the 40% category is not stated. |
| R02 | https://www.kaggle.com/competitions/iaa-ai-assisted-hackathon-2026-part-1/rules | General Rules, Determining Winners | 2026-10-18; Official — fresh | The general boilerplate says potential winners are determined solely by the private leaderboard. | This conflicts with the competition-specific two-part judging language and the overview. Do not silently choose a hierarchy; organiser clarification remains pending. |
| R03 | https://www.kaggle.com/competitions/iaa-ai-assisted-hackathon-2026-part-1/rules | Competition-Specific Rules, timeline and submission limits | 2026-10-18; Official — fresh | The current specific rule permits ten submissions per day and one final submission for judging. | Timeline fields remain `[DATE, TIME UTC]` placeholders. The older five-per-day statement in `docs/plan.md` is superseded for current planning by this fresh primary source but the page may change. |
| E01 | `docs/evidence/competition-sources.md` | Entire file | Prior verification dated 2026-10-18; Prior official extract | Preserves the prior metric, target, CSV and source-status summary and warns against silently resolving scoring or rules conflicts. | It is a secondary local record; fresh official retrieval above is preferred where available. |
| M01 | `docs/evidence/expected-manifest.json` and `docs/evidence/known-findings.md` | Manifest and audit summary | Measured — reverify | Records expected filenames/hashes and prior audit results, including 626,639 test rows, no ultimate label, exposure defects, linkage findings, recoveries and maturity indicators. | `IAA_DATA_DIR` is unset and hashes were not compared in Prompt 01, so none of these are promoted to current local measurements. |
| B01 | `context.md` | Objective, constraints and decisions | User brief; preserved unchanged | Records the desired end-to-end workflow, five-part communication blueprint, hybrid GLM/ML ensemble choice and governance aspirations. | It mixes user choices with unverified claims about official rules and professional mandates. |
| B02 | `what-good-looks-like.md` | Evaluation framework and evidence checklists | User quality brief; preserved unchanged | Records a quality bar including time-based validation, page-one findings and evidence-oriented AI oversight. | Some items are recommendations or professional interpretations rather than explicit organiser requirements. |
| P01 | `docs/plan.md` | Prediction contract, validation and conflict notes | Project interpretation; proposal pending human approval | Proposes conditional model comparison, earlier chronological folds plus a 2024 maturity challenge, and page-one findings/limitations. | It cannot override explicit user choices or resolve scoring and target uncertainty without evidence and human review. |
| I01 | `AGENTS.md` | Current scope; data and actuarial rules | Current user instruction | Establishes Prompt 01 scope, inclusive loss-date boundaries, expected net ultimate period cost, source precedence and the ban on executing later prompts. | It is an operating instruction, not an official competition page. |

## Exact published metric and submission illustration

The freshly retrieved evaluation page names the metric exactly as **“Tweedie D² score (power = 1.5)”**.

The published CSV illustration is:

```text
row_id, prediction
M02409311,583.47
B01834522,412.10
```

These establish the metric name, power and illustrated column order. They do not establish exact scorer code, pooling, weights or whether the competition implementation uses the same prediction-domain checks as a particular software library.

## Task in five plain sentences

1. Each prediction is for one 2025 policy-period row, rather than for a customer, a whole policy lifetime or an annual rate left unscaled.
2. A claim belongs to a row when its loss date falls within that row's covered period, using the project's explicit instruction that both boundaries are inclusive.
3. Ultimate cost means the eventual final cost of all claims arising in that row's period after reporting and development have run their course.
4. The model estimates an expected cost across possible outcomes; it does not guarantee the realised cost of an individual row.
5. The financial target is net of policy excess and recoveries, excludes declined claims, and represents risk premium rather than premium charged.

## Classification of current claims

### Official requirements

- Predict one expected ultimate claim cost for every `row_id` in the three 2025 test policy tables.
- Use loss date to associate a claim with its policy-period row.
- Submit one CSV with `row_id` and `prediction`; predictions must be nonnegative.
- The published metric name and power are fixed as quoted above, and higher is better.
- The four evaluation-category weights are 40/25/20/15; the report and video cutoffs are five pages and five minutes.
- Traditional actuarial models, machine learning and combinations are all allowed; no ensemble is mandated.

### Prior measured data findings requiring revalidation

- The prior audit records 626,639 test rows, no supplied ultimate label and one 31 December 2024 financial valuation.
- It also records ID, exposure, sum-insured, linkage, recovery, maturity, large-loss, contact, renewal and weather findings.
- These are measurements of earlier local files, not organiser guarantees, and are not current until the manifest hashes match.

### Interpretations and proposed methods

- Conditional GLM/ML comparison, chronological folds and maturity sensitivities are project recommendations.
- “Expected” is interpreted as a conditional mean, not a guaranteed row outcome.
- A developed target must distinguish observed incurred cost, unreported claims, reported-claim development and future recoveries; the official pages do not provide those quantities.
- Page-one findings, cards, explainability techniques and one-command reproducibility may be useful controls, but are not all stated as mandatory competition artifacts.

### Explicit user choices

- Preserve the original five-part communication blueprint and hybrid GLM/ML ensemble direction unless a proposed revision is approved.
- Apply inclusive loss-date boundaries and exposure exactly once.
- Preserve raw inputs, keep them outside Git and do not execute data corrections or model training in Prompt 01.

### Unresolved assumptions

- Exact scorer implementation, row/line pooling, exposure weighting and the numeric treatment of zero predictions.
- How private leaderboard scores and panel assessment combine inside the 40% performance category.
- Which rule text controls the conflict between competition-specific two-part judging and general private-leaderboard-only boilerplate.
- Case-reserve adequacy, unreported-loss completeness, future recoveries and the absence of a true ultimate label.
- Timing and prospective availability of contact, historical financial and annual weather fields.
- Professional-standard assertions in the original briefs until their primary sources are checked.

## Conflict register

| Conflict | Evidence | Current disposition | Human decision |
| --- | --- | --- | --- |
| Predetermined ensemble versus conditional comparison | `context.md` chooses a hybrid GLM/ML ensemble; the official overview merely permits multiple approaches; `docs/plan.md` proposes earning complexity through comparison. | Preserve the original choice as a design direction, but do not claim the ensemble is mandatory or selected by evidence. The conditional revision remains proposed. | Pending |
| Page-one layout | `context.md` starts page one with the Data Card; `what-good-looks-like.md` and `docs/plan.md` propose front-loading findings, target and limitations. | Preserve both records. Treat the findings-first layout as a proposed revision, not an approved replacement. | Pending |
| Immature 2024 holdout | The data page dates claims at 31 December 2024; the prior audit says no ultimate label and high 2024 open shares; the quality brief proposes a 2024 holdout. | A 2024 challenge cannot validate true ultimate cost by itself. Earlier folds and explicit maturity sensitivities are proposed safeguards. | Pending |
| Unverified mandatory-governance claims | `context.md` calls cards, SHAP and specific controls mandatory; current Kaggle pages require validation, reproducibility, governance and communication but do not mandate those exact artifacts or tools. | Retain them as user-selected or proposed controls. Do not attribute professional necessity until primary professional sources are checked. | Pending |
| Scoring semantics | Kaggle fixes the metric name/power and nonnegative submission domain; no retrieved source defines scorer code, pooling, exposure weights or all boundary behavior. | Keep pooling and weighting unresolved. Separate competition requirements from behavior of any standard-library implementation. | Pending |
| Rules/overview discrepancy | Overview and competition-specific rules use two-part scores plus panel judging; general rules say winners are determined solely by the private leaderboard. | Record the conflict without choosing a silent hierarchy or contacting organisers. | Pending |
| Daily submission limit in prior plan | `docs/plan.md` says five per day; the freshly retrieved competition-specific rule says ten. | Use ten as the current sourced limit when later planning submissions, while retaining the dated discrepancy and rechecking before any submission action. | Not a submission authorization |

## Prompt 01 boundary

No organiser was contacted, no terms were accepted, no data were downloaded or inspected, no contract code was written, and no later prompt was executed. Prompt 02 is next.
