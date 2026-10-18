# CONTEXT.md — IAA AI-Assisted Actuarial Hackathon 2026

## 1. Objective
* **What We Are Building**:
  * An end-to-end actuarial pricing pipeline and predictive model for an insurer in a developed market to estimate the expected ultimate claim cost (net of excess and recoveries, excluding declined claims) for 2025 policy rows across three lines of business: **Private Motor**, **Home Buildings**, and **Home Contents**.
  * A flexible model architecture and adaptation framework capable of adjusting to a new emerging-market dataset introduced in **Part 2**.
  * Four complete competition deliverables:
    1. **Written Report**: Maximum 5 pages (only first 5 pages graded).
    2. **Video Demo**: Maximum 5 minutes (only first 5 minutes graded).
    3. **Version-Controlled Code Repository**: Clean, modular GitHub repository.
    4. **Prediction Files**: `.csv` file containing predicted 2025 ultimate claim costs.
* **What Success Means**:
  * Achieving a top Tweedie $D^2$ score (power parameter $p = 1.5$) on the competition evaluation leaderboard.
  * Satisfying both automated AI review screeners and human judging panels across all 4 evaluation pillars:
    * **Pricing Performance & Adaptation** (40%)
    * **Effective Use of AI** (25%)
    * **Trust, Validation & Guardrails** (20%)
    * **Communication & Documentation** (15%)
  * Demonstrating strict adherence to professional actuarial governance standards (ISAP 1, PG 1) and IAA AI guidelines (AITF papers).

---

## 2. Confirmed Facts and Constraints
* **Dataset**:
  * Synthetic training data spanning policies from 2021 to 2024, with claims valued as of 31 December 2024.
  * Contains immature policies, open claims, and unreported claims requiring explicit IBNR and claims development treatment.
* **Evaluation & Metric**:
  * Primary metric: Tweedie $D^2$ deviance score ($p = 1.5$).
* **Deliverable Constraints**:
  * **Strict Page Limit**: Exactly the first 5 pages of the report are graded; any content beyond page 5 is ignored.
  * **Strict Video Limit**: Exactly the first 5 minutes of the video demo are graded.
  * **First-Pass Screening**: Automated AI review tools perform initial screening before human judges review submissions.
* **Governance & Professional Constraints**:
  * **Non-Delegable Accountability** (PG 1 Principle C, ISAP 1 Sec 2.3): The actuary retains full professional responsibility for all work products and code. Stating *"the AI generated the code"* is explicitly non-compliant as a defence.
  * **Human Oversight Required**: Implementation of Human-in-the-Loop or Human-on-the-Loop verification for all GenAI/LLM-generated code, data pipelines, and report text.
  * **Deterministic Verification**: AI-generated code must be validated via unit testing (`/tests`), JSON schema verification, and prompt/version logging (`PROMPT_LOGS.md`).
  * **Data & Model Governance**: Mandatory documentation including a **Data Card** (data provenance, IBNR assumptions, cleaning steps), **Model Card** (model selection, parameters, SHAP explainability), and **System Card** (operational controls).

---

## 3. Decisions and Reasons
* **Decision 1: Aligned 5-Page / 5-Minute Structural Blueprint**:
  * *Choice*: Structured the report, video demo, and repository around 5 core sections (Page 1: Data Governance/Data Card; Page 2: Pricing Architecture & Assumptions; Page 3: Model Card & Validation; Page 4: AI Verification & Code Governance; Page 5: Communication, Uncertainty & Part 2 Adaptation).
  * *Reason*: Guarantees complete coverage of all 4 judging criteria while optimizing for automated AI screening tools and respecting the strict 5-page / 5-minute cutoff.
* **Decision 2: Hybrid GLM + ML Ensemble with SHAP/LIME Explainability**:
  * *Choice*: Combine traditional Tweedie GLMs with Gradient Boosted Machines (GBMs) and hybrid ensembles, paired with SHAP/LIME feature importance diagnostics.
  * *Rejected Approach*: Black-box AutoML models without explainability. *Reason for Rejection*: ISAP 1 Section 2.10 and PG 1 Principle B mandate model transparency, validation, and explainability.
* **Decision 3: Active Data Drift & Concept Drift Diagnosis for Part 2**:
  * *Choice*: Build explicit distribution drift diagnostic scripts (`adaptation_analysis.py`) to evaluate how developed-market baseline assumptions shift in emerging markets.
  * *Rejected Approach*: Directly applying developed-market rating structures to emerging-market data without recalibration. *Reason for Rejection*: ISAP 1 Section 2.2 requires understanding relevant business/regulatory circumstances and re-evaluating baseline assumptions when entering new markets.
* **Decision 4: Automated Testing Framework for AI-Assisted Code**:
  * *Choice*: Implement automated unit testing (`pytest`), deterministic schema validation, and complete prompt history logging (`PROMPT_LOGS.md`).
  * *Rejected Approach*: Copying AI-generated code directly into production without verification. *Reason for Rejection*: Violates actuarial accountability standards (PG 1 Principle C, AITF Professional Considerations Paper Sec 3.5.1).

---

## 4. Current Status
* **Completed Work**:
  * Mapped competition rules to formal actuarial guidelines (PG 1 Principles A, B, C; ISAP 1 Sections 2.1, 2.2, 2.3, 2.5, 2.6–2.9, 2.10, 2.11, 3.1, 3.2).
  * Designed page-by-page 5-page report outline, 5-minute video storyboard, and GitHub repository structure (`DATA_CARD.md`, `MODEL_CARD.md`, `SYSTEM_CARD.md`, `/tests/`, `PROMPT_LOGS.md`).
  * Compiled Master Context Pack summarizing all technical and governance specifications.
* **Unresolved Issues / Pending Tasks**:
  * Ingesting synthetic policy/claims dataset and conducting initial Exploratory Data Analysis (EDA).
  * Formulating explicit claims development triangles and IBNR adjustment logic for open/immature claims.
  * Hyperparameter tuning for Tweedie GLM and LightGBM/XGBoost models using Tweedie $D^2$ loss ($p = 1.5$).
  * Creating automated PyTest unit tests for data transformation schemas and model output sanity checks.
  * Evaluating Part 2 emerging-market dataset upon release.
* **Next Action**:
  * Set up GitHub repository architecture, execute `data_prep.py` for data cleaning and IBNR estimations, and populate `DATA_CARD.md`.

---

## 5. Source References
* **IAA Principles of Professionalism (PG 1)**:
  * *Principle A (Knowledge & Expertise)*, *Principle B (Values & Behaviour)*, *Principle C (Professional Accountability)*.
* **International Standard of Actuarial Practice 1 (ISAP 1: General Actuarial Practice)**:
  * *Sec 2.1 (Acceptance of Assignment)*, *Sec 2.2 (Knowledge of Relevant Circumstances)*, *Sec 2.3 (Reliance on Others)*, *Sec 2.5 (Data Quality)*, *Sec 2.6–2.9 (Assumptions & Methodology)*, *Sec 2.10 (Model Governance)*, *Sec 2.11 (Process Management)*, *Sec 3.1 & 3.2 (Communication)*.
* **IAA AI Task Force (AITF) Papers**:
  * *AITF Governance Framework Paper (2025)*: AI lifecycle governance, Model Owner roles, independent validation.
  * *AITF Documentation of AI Models Paper (2025)*: Data Card, Model Card, and System Card standards.
  * *AITF Professional Considerations Paper (2026)*: Non-delegable accountability (Sec 3.5.1), Human-in-the-Loop oversight, prompt logging.
  * *Model Governance and Ethics for GenAI Models (2026)*: Deterministic JSON checks, agentic workflows, unit testing for AI code.
