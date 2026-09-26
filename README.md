A Decision-Theoretic Extension of Causal Unit Selection

Overview

This repository contains the official Python replication code and supplementary computational materials for the research preprint:

A Decision-Theoretic Extension of Causal Unit Selection: Identifiability, Threshold Rules, and the Fallacy of Naive Benefit Rates

Author: Joona Matti Ensio Eskelinen
Year: 2026
Current version: Version 4 / Final
Zenodo DOI (Final Version 4): https://doi.org/10.5281/zenodo.22962244
Zenodo DOI (all versions): https://doi.org/10.5281/zenodo.22934160

The framework extends causal unit selection into a decision-theoretic setting under counterfactual uncertainty. It develops explicit decision and abstention rules, studies their statistical reliability, extends the framework to AI-agent autonomy decisions, and analyzes strategic adaptation when deployed decision rules become observable to the environment.

Version 4 extends the Version 3 autonomy framework to strategic environments. It studies how observable success margins may become endogenous after deployment and examines when post-deployment re-estimation restores the safety properties of the original autonomy gate.

The full Version 4 preprint is permanently archived on Zenodo.

⸻

Core Contributions

The framework develops the following main theoretical results.

Theorem 5 — Identifiability

The target benefit function is point-identifiable purely from observable causal effects if and only if the structural master coefficient

σ = β − γ − θ + δ

equals zero.

When σ ≠ 0, counterfactual shifts can alter the true benefit function while leaving observable causal margins unchanged.

Theorem 6 — Decision Criterion and Abstention

Under fundamental counterfactual uncertainty where the Probability of Necessity and Sufficiency (PNS) is unknown, target groups are strictly decidable if and only if

|W₁ − W₀| > |σ|.

When this condition fails, the structural intervals overlap and the rule abstains from selection.

Theorem 7 — Reliability Under Estimation

For a true gap margin

D = |W₁ − W₀| − |σ| > 0,

the decision rule yields zero active errors asymptotically, with the required empirical sample size scaling proportionally to 1 / D².

When D ≤ 0, additional data alone cannot resolve the underlying structural uncertainty.

Theorem 8 — Autonomy Criterion

Extending the framework to agent environments, an agent’s action is strictly and decidably better than deferring to a human baseline if and only if

|γ − δ| · |pₐ − pₕ| > |σ|,

where pₐ denotes the agent success rate and pₕ denotes the human success rate.

Theorem 9 — Abstain Safety

Under the autonomy criterion, the structural margin forces the system to defer when the observable advantage is insufficient to overcome the utility uncertainty represented by |σ|.

The harm parameter δ directly affects this structural margin, allowing the gate to encode different risk tolerances through explicit utility parameters rather than heuristic confidence thresholds.

⸻

Strategic Extension — Version 4

Version 4 studies the autonomy rule as a Stackelberg interaction.

A defender commits to a decision rule while a strategic follower observes that rule and may adapt through mechanisms such as:

* evasion,
* feature inflation,
* threshold gaming, or
* other strategic responses.

As a consequence, the observable margins pₐ and pₕ may themselves depend on the deployed policy.

The structural utility parameter σ remains fixed. What changes are the observable margins and the effective uncertainty created by strategic adaptation.

Two strategically different cases are distinguished:

Performance degradation tends to close the autonomy gate and push the system toward abstention.

Performance inflation can be more problematic because observable performance may improve while underlying true risk remains unchanged, potentially causing a stale decision rule to grant autonomy incorrectly.

Theorem 10 — Abstain Robustness Under Strategic Adaptation

Version 4 compares two regimes:

1. Naive deployment: the autonomy gate continues using pre-deployment or stale parameters after the environment adapts.
2. Robust deployment: the relevant margins are re-estimated after strategic response and the decision rule is iterated toward a fixed point.

The computational experiments show that stale-parameter deployment can produce non-zero active error under strategic adaptation, while re-estimation restores zero active error in the tested configurations.

Theorem 11 — Strategic Stability of Abstention

If the rule enters the ABSTAIN state, strategic effort directed specifically at the autonomous agent’s threshold loses its payoff.

For adversarial utility

U(e) = P(agent decision passes | e) · V − c · e,

under ABSTAIN the autonomous agent does not produce the final decision, so

P(agent decision passes | e) = 0.

Therefore,

U(e | ABSTAIN) = −c · e,

which is maximized at e* = 0.

Under the stated strategic model, abstention therefore functions both as a safety state and as a mechanism that removes the incentive to exert effort against the autonomous threshold.

Theorem 12 — Convergence of Re-estimation

Under the stated monotonic strategic-response assumptions, Version 4 studies the iterative rule

τₜ₊₁ = F(τₜ).

The computational implementation evaluates both linear and logistic/saturating response families.

Across three response scales and five starting conditions for each family, all 30 evaluated computational runs converged to the same observed fixed point, q* ≈ 0.999, with zero active error in the tested runs.

The result establishes convergence under the stated monotonic setting. It does not establish general uniqueness of the fixed point.

Theorem 13 — Zero Active Error at Equilibrium

At a fixed point τ*, the rule is evaluated using the same equilibrium margins generated under that rule.

The resulting state therefore either:

* ABSTAINS, producing no autonomous active error, or
* ACTS when the T8 criterion is satisfied using the equilibrium margins.

Under the assumptions of the framework:

active error(τ*) = 0.

⸻

Empirical and Computational Validation

The framework is evaluated across several domains and datasets.

TWINS

The original causal unit-selection framework was validated using the Louizos et al. TWINS dataset (n = 71,345).

The analysis illustrates the structural limitation of the naive benefit rate

PNS − P(H).

In the evaluated high-risk preterm stratum, the naive metric is approximately 0.19%, while the true benefit rate is approximately 2.7%, producing an approximately 14-fold underestimation because true benefit and active harm cancel in the aggregate.

Financial Markets

The framework was transferred to trading decisions using synthetic segmentations and approximately three years of public financial-market data across 380 non-overlapping decision units.

The experiments demonstrate how additional counterfactual information can tighten structural uncertainty and allow the benefit interval to bound true utility outside clinical settings.

LLM Guardrail Validation — FiFAR / OpenL2D

The Version 3 autonomy gate was evaluated using a public fraud dataset with AI decisions and 50 synthetic human analysts across n = 30,622 cases.

The T8/T9 gate correctly executed all 54 evaluated segment decisions between ACT and ABSTAIN in the reported experiments.

Version 4 revisits FiFAR specifically as a strategic-feedback stress test.

The dataset exhibits a strong baseline imbalance: fraud prevalence is approximately 12%, giving a trivial majority-class accuracy of approximately 88%. In the tested setup, the human analysts are substantially below this level.

This creates an informative negative result: the tested strategic perturbation is unable to push the AI below the human comparison boundary, making the autonomy decision structurally robust in this tested regime.

This illustrates an important scope condition of the Version 4 analysis: strategic feedback becomes most consequential near narrow decision margins. Large performance separations or sufficiently wide structural margins can make the autonomy gate robust before iterative correction is required.

Lending Club

Version 4 introduces an additional real-data strategic validation using approximately 1.34 million completed Lending Club loans, with an observed default rate of approximately 20%.

Credit quality meaningfully discriminates risk in the evaluated data, with default rates ranging approximately from 26.8% to 11.1% across the relevant credit-quality range.

The strategic simulation models feature inflation in which observable, potentially gameable variables improve while underlying true risk does not necessarily improve correspondingly.

The results depend strongly on the structural margin.

For the evaluated narrow-margin σ = 0 configurations, the stale-parameter rule fails in 9–11 of 12 tested cases across three configurations, while re-estimation produces zero active errors.

For the evaluated wider-margin σ = 20 configuration, the available strategic improvement is insufficient to reverse the decision, so the naive rule does not fail in the tested setup while the robust rule again produces zero active errors.

These results support the narrower interpretation of the Version 4 finding: strategic adaptation is most consequential near the autonomy boundary rather than uniformly across all decision regimes.

⸻

Stackelberg Verification

The strategic response is also examined directly.

In the evaluated setup, the observed pₐ response is monotonic, decreasing from approximately 0.717 to 0.237 across the relevant threshold range.

Across five starting points, the iteration converges to approximately

τ* = 0.116

within 5–7 iterations.

At the resulting ACT fixed point:

* pₐ ≈ 0.704
* pₕ ≈ 0.317

and the equilibrium autonomy decision has zero active error in the tested configuration.

A placebo negative control does not reproduce the same convergence behavior, providing an additional computational check that the observed fixed point is associated with the modeled strategic response rather than being an automatic artifact of the iteration.

⸻

Open Mathematical Boundary

Version 4 deliberately distinguishes convergence from uniqueness.

The T12 result establishes convergence under the stated monotonic assumptions but does not prove that a fixed point is unique over the entire monotonic response class.

The empirically measured Lipschitz constants of the update mapping range approximately from 1.10 to 1.74 in the evaluated configurations.

Because all measured values exceed 1, the mapping is not a contraction in these tests, and the Banach fixed-point theorem cannot be used to establish general uniqueness.

Empirically, all 30 evaluated starting conditions converge to the same observed fixed point, but general uniqueness remains an open mathematical boundary rather than a claimed theorem.

⸻

Scope and Limitations

Theorems T10–T13 are strategic extensions and corollaries built on the T5–T9 decision structure rather than replacements for the original causal framework.

The convergence result in T12 relies on a monotonic strategic-response assumption.

Non-monotonic strategic responses remain outside the present convergence result, although the strategic-stability argument of T11 does not require monotonicity.

The human baseline pₕ used in strategic simulations is a calibration parameter designed to create controlled autonomy-boundary experiments and should not be interpreted as a general empirical estimate of real human performance.

The Lending Club strategic simulation is intentionally simplified and uses a stylized risk and feature-improvement mechanism. Its purpose is to test the mathematical behavior of the autonomy rule under endogenous strategic response, not to provide a production credit-scoring model.

The computational results reported in this repository establish behavior in the tested configurations and should not be interpreted as proofs beyond the assumptions explicitly stated in the preprint.

⸻

Repository Structure

.
├── core/
│   └── unit_selection_theorems.py
├── replication_scripts/
│   ├── market_validation_scripts.py
│   ├── v3_guardrail_validate.py
│   └── v4_validate.py
├── A_Decision_Theoretic_Extension_of_Causal_Unit_Selection_v4.pdf
├── CITATION.cff
├── LICENSE
├── README.md
└── requirements.txt

A_Decision_Theoretic_Extension_of_Causal_Unit_Selection_v4.pdf

Full Version 4 preprint containing T5–T9, the LLM Agent Autonomy Guardrail, the strategic Stackelberg extension, Theorems T10–T13, real-data validation, convergence experiments, and the documented open uniqueness boundary.

core/unit_selection_theorems.py

Core implementation of the causal unit-selection bounding theorems and associated computational framework.

replication_scripts/market_validation_scripts.py

Replication code for the synthetic financial-market DGP and public yfinance validation.

replication_scripts/v3_guardrail_validate.py

Version 3 replication script for the T8/T9 LLM autonomy gate, including the original Monte Carlo and dataset validation procedures.

replication_scripts/v4_validate.py

Version 4 validation script containing the strategic-response experiments and computational verification for the Version 4 extension, including:

* T10 robustness experiments,
* T12 fixed-point and convergence checks,
* strategic FiFAR evaluations,
* Lending Club evaluations,
* Stackelberg verification,
* negative controls, and
* numerical investigation of the open uniqueness boundary.

No additional Version 4 replication scripts are required beyond v4_validate.py. Version 4 builds on the existing Version 3 replication files and the core theorem implementation.

⸻

Reproducibility

The Python scripts in this repository provide the computational experiments and replication procedures associated with the preprint.

Python dependencies are listed in requirements.txt.

Some validations rely on external public datasets or data sources. Users should obtain any required third-party datasets in accordance with their respective licenses and terms of use.

The permanently archived research record, including the Version 4 preprint and replication scripts, is available through Zenodo:

Final Version 4:
https://doi.org/10.5281/zenodo.22962244

All versions / latest version:
https://doi.org/10.5281/zenodo.22934160

⸻

Version History

Version	Zenodo DOI
Version 1.0.0	https://doi.org/10.5281/zenodo.22934161
Version 2	https://doi.org/10.5281/zenodo.22953924
Version 3	https://doi.org/10.5281/zenodo.22958342
Version 4 / Final	https://doi.org/10.5281/zenodo.22962244
All versions	https://doi.org/10.5281/zenodo.22934160

The current repository and GitHub release correspond to Version 4 / Final of the preprint.

⸻

Citation

If you use this framework, source code, or replication material, please cite the associated preprint:

Eskelinen, J. M. E. (2026). A Decision-Theoretic Extension of Causal Unit Selection: Identifiability, Threshold Rules, and the Fallacy of Naive Benefit Rates. (Version Final). Zenodo. https://doi.org/10.5281/zenodo.22962244

Citation metadata is also provided in CITATION.cff.

For references intended to resolve to the latest version of the work, use the all-versions DOI:

https://doi.org/10.5281/zenodo.22934160

⸻

License

Copyright © 2026 Joona Matti Ensio Eskelinen.

The materials in this repository are made available under the Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) license.

You may share and adapt the licensed material for non-commercial purposes, provided appropriate attribution is given and the applicable license terms are followed.

Commercial use is not permitted under CC BY-NC 4.0.

See the LICENSE file for license information.

For commercial licensing, commercial implementation, or permissions beyond the scope of CC BY-NC 4.0, contact the copyright holder.

⸻

Permanent Research Record

The authoritative archived research record is maintained on Zenodo.

Final Version 4
https://doi.org/10.5281/zenodo.22962244

All versions / persistent concept DOI
https://doi.org/10.5281/zenodo.22934160
