# Step 4 — Implement chronological validation

Imported from `IAA_Step4_Prompt_Algorithm.md` supplied 19 October 2026. It defines eight prompts, S4-00 through S4-07, to establish calendar folds, feature availability, fold-safe views, scoring, a framework runner, challenge review and acceptance. Step 4 is a validation-framework stage only: it must not train/tune pricing models, create 2025 predictions or submit.

The monetary experiment is a `retrospective_snapshot_proxy`: all available financial amounts have a 31 December 2024 valuation, even where feature/transformation cutoffs emulate earlier prediction dates. The contract uses F2022 (train 2021/validate 2022), F2023 (train 2021–2022/validate 2023, primary) and F2024 (train 2021–2023/validate 2024, challenge). Full prompt text is reproduced in `prompts/step4/`.
