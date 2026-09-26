# A Decision-Theoretic Extension of Causal Unit Selection

Official Python replication code and supplementary materials for the paper: **"A Decision-Theoretic Extension of Causal Unit Selection: Identifiability, Threshold Rules, and the Fallacy of Naive Benefit Rates"**.

<p align="left">
  <a href="https://zenodo.org/records/22962244">
    <img src="https://shields.io" alt="Zenodo Record">
  </a>
  <a href="https://creativecommons.org/licenses/by-nc/4.0/deed.en">
    <img src="https://shields.io" alt="License">
  </a>
</p>


---

## Overview

This repository provides the computational frameworks and empirical validation scripts for evaluating generalized causal unit selection under counterfactual uncertainty. It addresses asymmetric utility optimization, automated decision boundaries, and structural risk management.

### Cross-Disciplinary Applicability
While evaluated primarily within strategic classification contexts, the underlying mathematical architecture (Theorems 10–13 in Version 4) is domain-agnostic and generalizes directly to:
* **Precision Medicine:** Mitigating the *Fallacy of Naive Benefit Rates* in personalized clinical trial designs using multi-outcome differential patient utilities (validated via the TWINS dataset).
* **Adaptive Control Systems & Cyber-Physical Engineering:** Acting as a mathematical fail-safe (*ABSTAIN* state) to maintain system equilibrium under dynamic environmental perturbations or degraded telemetry.

---

## Replication & Usage

To replicate the empirical results presented in the paper (including the TWINS and Lending Club analyses), ensure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

*(Add brief instructions here on how to run your main Python script, e.g., `python main.py`)*

---

## Citation

If you use this framework, the replication code, or references to the generalized decision-theoretic extensions in your research, please cite the permanent Zenodo record:

```bibtex
@preprint{eskelinen2026decision,
  title={A Decision-Theoretic Extension of Causal Unit Selection: Identifiability, Threshold Rules, and the Fallacy of Naive Benefit Rates},
  author={Eskelisen, Joona},
  year={2026},
  month={September},
  publisher={Zenodo},
  version={Version 4},
  doi={10.5281/zenodo.22962244},
  url={https://doi.org}
```

---

## License

This repository and all its content (including code, data structures, and documentation) are licensed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license. 

* **Commercial usage is strictly prohibited** without prior explicit consent from the author.
* Any derivatives or forks must maintain proper attribution and reference the original work.
