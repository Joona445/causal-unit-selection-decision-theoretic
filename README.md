# A Decision-Theoretic Extension of Causal Unit Selection

Official Python replication code and supplementary materials for the paper: **"A Decision-Theoretic Extension of Causal Unit Selection: Identifiability, Threshold Rules, and the Fallacy of Naive Benefit Rates"** [22962244].

---

## Overview

This repository provides computational frameworks and empirical validation scripts for evaluating generalized causal unit selection under counterfactual uncertainty, addressing asymmetric utility optimization and automated decision boundaries. The full theoretical text and mathematical proofs can be read in the root file: **`A_Decision_Theoretic_Extension_of_Causal_Unit_Selection_v4.pdf`** [22962244].

### Cross-Disciplinary Applicability
The mathematical architecture generalizes directly to fields such as **Precision Medicine** and **Adaptive Control Systems & Cyber-Physical Engineering** [22962244].

---

## Repository Structure

*   `/core`: Contains `unit_selection_theorems.py` implementing foundational mathematical constraints and bounding algorithms [22962244].
*   `/replication_scripts`: Contains simulation and empirical evaluation protocols (`v4_validate.py`, `v3_guardrail_validate.py`, `market_validation_scripts.py`) [22962244].

---

## Replication & Usage

Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Running the Validations
Execute the validation scripts from the repository root [22962244]:
* **Version 4 Verification:** `python replication_scripts/v4_validate.py` [22962244]
* **Version 3 Guardrail Validation:** `python replication_scripts/v3_guardrail_validate.py` [22962244]
* **Financial Market Validation:** `python replication_scripts/market_validation_scripts.py` [22962244]

---

## Citation & License

Please cite the permanent Zenodo record when using this framework [22962244]. Licensed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license [22962244].
