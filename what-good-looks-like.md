# IAA AI-Assisted Actuarial Hackathon 2026: "What Good Looks Like"

This document provides a comprehensive breakdown of the judging expectations, underlying competencies, evidence standards, and execution criteria for the **IAA AI-Assisted Actuarial Hackathon 2026**.

---

## Executive Summary & Core Ambition

The competition assesses **supervised delegation**: whether an actuary can direct artificial intelligence across a complex pricing workflow while taking full professional responsibility for the result. The primary objective is to produce a solution that **another actuary can understand, pick up, use, and trust**.

---

## Official Judging Criteria Breakdown

The evaluation framework consists of four explicit criteria, balancing predictive modeling, workflow design, risk control, and communication.

```
       ┌─────────────────────────────────────────────────────────────┐
       │               IAA 2026 Judging Rubric                       │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         │                            │                            │
   ┌─────┴─────┐                ┌─────┴─────┐                ┌─────┴─────┐
   │ Performance│                │ Effective │                │  Trust &  │
   │ & Adapt.  │                │ AI Use    │                │ Guardrails│
   │   (40%)   │                │   (25%)   │                │   (20%)   │
   └─────┬─────┘                └─────┬─────┘                └─────┬─────┘
         │                            │                            │
         └────────────────────────────┼────────────────────────────┘
                                      │
                                ┌─────┴─────┐
                                │ Comm. &   │
                                │  Doc.     │
                                │   (15%)   │
                                └───────────┘
```

---

## Detailed Evaluation Framework

### 1. Pricing Performance & Adaptation (40%)

* **Weight:** 40% (Combines equal-weighted private leaderboard scores across Part 1 and Part 2 with qualitative panel assessment).
* **Underlying Competency:** Translating complex insurance data into defensible pricing models; handling data quality, reserves, and development; recognizing when assumptions fail across new markets.

#### Evidence Checklist
* **Target Construction:** Explicit conversion from incurred claims to ultimate claims cost (net of excess/recoveries, excluding repudiated claims).
* **Development & IBNR:** Per-peril development factors (e.g., bodily injury vs. glass/theft) and explicit allowance for unreported/developing 2024 claims.
* **Validation Design:** Time-based holdout (e.g., train $\le 2023$, validate $2024$) rather than random $K$-fold cross-validation.
* **Calibration:** Actual-vs-Expected ($A/E$) analysis by line, region, and segment alongside Tweedie $D^2$.
* **Adaptation (Part 2):** Automated data-profile diffs, re-testing assumption registers, and explicit numerical adjustments for emerging market characteristics.

#### Weak vs. Strong Execution
| Execution Level | Characteristics |
| :--- | :--- |
| **Weak Execution** | Training directly on incurred-to-date claim amounts; using random $K$-fold CV (leaking multi-year policy rows); unexplained feature engineering; silently re-running the Part 1 pipeline on Part 2 data without re-evaluating assumptions. |
| **Strong Execution** | Credible ultimate target construction with explicit IBNR handling; time-based holdout validation; aggregate $A/E$ calibration checks; visible adaptation log documenting what changed between Part 1 and Part 2. |

---

### 2. Effective Use of AI (25%)

* **Weight:** 25%
* **Underlying Competency:** Supervised delegation, prompt engineering, challenging AI recommendations, and rigorous output verification.

#### Evidence Checklist
* **Direction Log:** A structured record mapping: `Task` $\rightarrow$ `AI Proposal` $\rightarrow$ `Human Challenge/Verification` $\rightarrow$ `Decision` $\rightarrow$ `Observed Impact`.
* **Caught AI Errors:** Explicit documentation of at least one instance where an AI error (e.g., target encoding leakage, improper policy joining) was caught and corrected by human oversight.
* **Adversarial AI Testing:** Using AI to generate invariant checks, unit tests, or edge-case diagnostics.

#### Weak vs. Strong Execution
| Execution Level | Characteristics |
| :--- | :--- |
| **Weak Execution** | Raw transcript dumps showing "ChatGPT wrote the notebook"; claiming unverified 60% efficiency gains without documentation. |
| **Strong Execution** | Clear evidence of human oversight; structured decision log highlighting caught AI errors; verified improvements in analytical reliability and efficiency. |

---

### 3. Trust, Validation & Guardrails (20%)

* **Weight:** 20%
* **Underlying Competency:** Model governance, process auditability, reproducibility, and risk controls.

#### Evidence Checklist
* **One-Command Reproducibility:** Single-command execution (e.g., via `Makefile` or script) rebuilding predictions from scratch with pinned dependencies, fixed random seeds, and verified output CSV hashes.
* **Automated Data Contracts:** Schema, value range, and exposure checks integrated into continuous integration (CI) tests.
* **Human Oversight Triggers:** Clear escalation rules detailing when human review is required and what specific actions were taken.

#### Weak vs. Strong Execution
| Execution Level | Characteristics |
| :--- | :--- |
| **Weak Execution** | Notebooks relying on hidden cell state; governance statements repeating standard implementation logic; missing audit trails. |
| **Strong Execution** | Fully reproducible pipeline; automated invariant testing suite; explicit human override log; clear statement of model limitations. |

---

### 4. Communication & Documentation (15%)

* **Weight:** 15% (Strict limits: first 5 report pages and first 5 video minutes graded).
* **Underlying Competency:** Concise technical communication, structured reporting, and transparent risk disclosure.

#### Evidence Checklist
* **Rubric-Matched Headings:** Report sections matching official judging criteria for initial AI screening and human panel review.
* **Page 1 Key Findings:** Front-loading key results, target definitions, and limitations on the first page.
* **Live Pipeline Video:** Demonstrating the running codebase, automated test suite, and prediction regeneration rather than theoretical slide decks.

#### Weak vs. Strong Execution
| Execution Level | Characteristics |
| :--- | :--- |
| **Weak Execution** | Lengthy introductory narratives pushing core results past page 5; video focusing solely on background slides rather than workflow execution. |
| **Strong Execution** | Highly structured 5-page report with rubric-aligned headings; video demonstrating live pipeline execution and test verification. |

---

## Summary of Strategic Priorities & Common Pitfalls

### Top 5 Priorities for a Winning Submission
1. **Construct the Target Properly:** Build ultimate claim costs with per-peril development factors and explicit AY2024 IBNR allowances.
2. **Implement Time-Based Validation:** Avoid data leakage by using temporal splits ($ train \le 2023$, $validate = 2024$) and checking aggregate calibration ($A/E$).
3. **Maintain a Direction & Verification Log:** Document human oversight with concrete examples of AI proposals, challenges, and caught errors.
4. **Ensure 1-Command Rebuilds:** Provide pinned environment files, seeds, unit test suites, and exact submission file hashes.
5. **Treat Part 1 as an Adaptable Method:** Build automated profile diffs and assumption registers to adapt smoothly to Part 2 emerging market data.

### Top 5 Pitfalls to Avoid
1. **Modelling Incurred-to-Date Claims Directly:** Ignoring claims development and reporting lags.
2. **Leaking Validation Data:** Using random $K$-fold cross-validation across multi-year policy records.
3. **Unverified AI Delegation:** Submitting generated code without documented human verification or error catches.
4. **Burying Evidence Past Cutoffs:** Placing key results beyond page 5 of the report or minute 5 of the video.
5. **Static Part 2 Execution:** Blindly re-running Part 1 models on emerging market data without adapting assumptions.
