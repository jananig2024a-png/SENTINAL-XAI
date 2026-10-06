# Sentinel XAI

### Evidence-Grounded and Agreement-Aware Explainable Network Intrusion Detection with Controlled LLM-Assisted Reporting

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Sentinel XAI is an explainable network intrusion detection system (NIDS) built around a strict separation between **deterministic security evidence** and **natural-language presentation**.

The system uses a Random Forest detector trained on **30 selected CICIDS2018 flow features**, generates local explanations using **SHAP and LIME**, measures explanation overlap using **Jaccard similarity**, and uses a bounded local **SmolLM2** layer only for readability. The language model is not treated as the authority for the security decision.

---

## 1. Project Overview

Traditional machine-learning NIDS models can achieve strong detection performance, but a prediction alone does not necessarily provide an analyst with compact and inspectable evidence.

Sentinel XAI addresses this by separating the workflow into four stages:

1. **Detection** — Random Forest predicts the traffic class and confidence.
2. **Evidence generation** — SHAP and LIME explain the same flow.
3. **Agreement measurement** — normalized top-10 SHAP and LIME feature sets are compared using Jaccard similarity.
4. **Controlled reporting** — a local SmolLM2 model produces only a bounded natural-language bridge phrase. Prediction, confidence, feature evidence, Jaccard value, and review wording remain deterministic.

If the generated language does not satisfy the evidence contract, the system can use a deterministic fallback rather than allowing unsupported model-generated claims to become security evidence.

---

## 2. System Architecture

```text
                    CICIDS2018 Flow Record
                              |
                              v
                 +-------------------------+
                 |  Random Forest Detector |
                 |  30 selected features   |
                 +------------+------------+
                              |
                 Prediction + Confidence
                              |
              +---------------+---------------+
              |                               |
              v                               v
        +-----------+                   +-----------+
        |   SHAP    |                   |   LIME    |
        | Top-10    |                   | Top-10    |
        +-----+-----+                   +-----+-----+
              |                               |
              +---------------+---------------+
                              |
                              v
                  Jaccard Similarity
                              |
                              v
                Agreement / Review Signal
                              |
                              v
                 +-------------------------+
                 | Controlled SmolLM2      |
                 | Presentation Layer      |
                 +------------+------------+
                              |
                              v
                    Evidence-Checked
                       Explanation
                              |
                  +-----------+-----------+
                  |                       |
             Accepted phrase        Deterministic
                                    fallback
```

### Evidence authority

The security record is deterministic:

- predicted class
- confidence
- SHAP feature evidence
- SHAP values/directions
- LIME feature evidence
- Jaccard similarity
- agreement/review wording



---

## 3. Dataset

The project is based on the **CICIDS2018** intrusion-detection dataset.

The repository does **not** include the raw CICIDS2018 dataset because of its size and redistribution considerations.

The preprocessing pipeline removes identifying/non-model fields and prepares the flow-level features required by the trained detector.

### Feature selection

The final detector operates on **30 selected flow features**.

Feature selection is performed using the training data so that the held-out test data is not used to select the model features.

---

## 4. Detection Model

The deterministic detection layer uses a **Random Forest classifier**.

The verified held-out test results reported by the project are:

| Metric | Test Result |
|---|---:|
| Accuracy | **99.9708%** |
| Macro Precision | **0.9338** |
| Macro Recall | **0.9354** |
| Macro F1 | **0.9345** |

The model artifact is provided separately in:

```text
models/RandomForest_NIDS.pkl
```

Supporting artifacts:

```text
models/Selected_Features.pkl
models/LabelEncoder.pkl
```

---

## 5. Explainability

Sentinel XAI generates explanations for the same local flow using:

- **SHAP** for feature attribution
- **LIME** for local surrogate-based explanation

The top-10 feature sets from both methods are normalized before comparison.

### Jaccard similarity

The explanation overlap is calculated as:

\[
J(A,B)=\frac{|A\cap B|}{|A\cup B|}
\]

where:

- `A` = normalized top-10 SHAP feature set
- `B` = normalized top-10 LIME feature set

The controlled explanation study reported:

- Mean Jaccard similarity: **0.3542**
- Minimum: **0.1765**
- Maximum: **0.6667**
- Operational manual-review threshold: **0.40**

The threshold is used as an operational review signal rather than as a claim that one explanation method is universally correct.

---

## 6. Controlled LLM-Assisted Reporting

Sentinel XAI uses a local **SmolLM2-1.7B-Instruct** model as a bounded presentation component.

The LLM receives deterministic evidence and is constrained to produce a short bridge phrase rather than independently deciding:

- the attack class
- the confidence
- the explanation features
- the Jaccard value
- the review decision

The generated phrase is checked against an evidence contract.

The reported controlled evaluation contains:

- **90 controlled samples**
- **90/90 accepted phrases**
- **0 fallbacks**
- automatic checks preserving deterministic evidence
- a **25-sample rubric** for factual consistency, agreement correctness, and readability

The large GGUF model file is intentionally not stored in this repository. This keeps the repository suitable for Git hosting and avoids committing a very large model artifact.

---

## 7. Repository Structure

```text
sentinel-xai/
│
├── README.md
├── CITATION.cff
├── LICENSE
├── .gitignore
├── app.py
│
├── backend/
│   └── ...
│
├── templates/
│   └── ...
│
├── static/
│   └── ...
│
├── models/
│   ├── RandomForest_NIDS.pkl
│   ├── Selected_Features.pkl
│   └── LabelEncoder.pkl
│
├── evaluation/
│   └── 06_LLM_XAI_Evaluation.py
│
├── evidence/
│   └── Contribution3_XAI_Evidence.json
│
├── outputs/
│   ├── 90_sample_evaluation.csv
│   └── 90_sample_faithfulness_check.csv
│
└── figures/
    ├── confusion_matrix.png
    └── jaccard_histogram.png
```

### Important

Raw datasets, secrets, temporary files, and the large local GGUF model should not be committed.

In particular, the repository should not contain:

- CICIDS2017 cross-dataset evaluation files
- raw CICIDS2018 data
- `.env` files
- API keys or credentials
- Google Drive/Colab paths
- `.ipynb_checkpoints`
- `__pycache__`
- the large SmolLM2 GGUF artifact

---

## 8. Installation

Clone the repository and create a Python environment.

```bash
git clone <https://github.com/JANANI2025/SENTINEL-XAI>
cd sentinel-xai
```

Create a virtual environment:

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r backend/requirements.txt
```

---

## 9. Running the Web Application

Start the Flask application:

```bash
python app.py
```

The application provides the Sentinel XAI interface for intrusion detection and explanation.

The trained model and supporting preprocessing artifacts are loaded from the `models/` directory.

If the optional local LLM component is enabled, its model file must be supplied separately and configured according to the application code. The large GGUF file is intentionally excluded from Git.

---

## 10. Evaluation

The repository contains the evaluation implementation and derived evidence required to inspect the reported explanation workflow.

Main evaluation script:

```text
evaluation/06_LLM_XAI_Evaluation.py
```

Evidence:

```text
evidence/Contribution3_XAI_Evidence.json
```

Evaluation outputs:

```text
outputs/90_sample_evaluation.csv
outputs/90_sample_faithfulness_check.csv
```

The evaluation checks deterministic values including prediction, confidence, Jaccard similarity, SHAP evidence, agreement/review wording, and compliance of the generated language.

---

## 11. Figures

The repository includes the principal visual outputs used with the project:

```text
figures/confusion_matrix.png
figures/jaccard_histogram.png
```

These figures should remain synchronized with the final version of the research paper.

---

## 12. Reproducibility and Evidence

The repository is organized so that the trained detector, selected features, label encoding, evaluation implementation, explanation evidence, derived evaluation outputs, and figures can be inspected separately.

The design deliberately distinguishes:

**Authoritative evidence**
- trained detector output
- confidence
- SHAP/LIME evidence
- Jaccard calculation
- deterministic review wording

**Presentation**
- controlled LLM bridge phrase

This separation is central to the Sentinel XAI workflow.

---

## 13. Limitations

- The system is evaluated on CICIDS2018 and should not be interpreted as universally representative of all network environments.
- The reported performance is benchmark performance and does not by itself establish deployment-level security effectiveness.
- SHAP and LIME are post-hoc explanation methods and their agreement is measured operationally rather than treated as a complete measure of explanation truth.
- The local LLM is used for readability and is deliberately prevented from becoming the authoritative security decision layer.
- The raw dataset and large local language-model artifact are not distributed with this repository.

---

## 14. Research Artifact

This repository accompanies the research work:

**Sentinel XAI: Evidence-Grounded and Agreement-Aware Explainable Network Intrusion Detection with Controlled LLM-Assisted Reporting**

The project demonstrates an evidence-first workflow in which language generation improves accessibility while deterministic security evidence remains authoritative.

---

## 15. Citation

If you use this software, please cite the repository using the citation information in [`CITATION.cff`](CITATION.cff).

### BibTeX

```bibtex
@software{sentinel_xai_2026,
  title  = {Sentinel XAI: Evidence-Grounded and Agreement-Aware Explainable Network Intrusion Detection with Controlled LLM-Assisted Reporting},
  author = {Janani G and D Deepa and Aqsha Fathima I and Gayathri M and Rakshitha N and Syed Fazila Musquan},
  year   = {2026},
  version = {1.0.0},
  url    = {<https://github.com/JANANI2025/SENTINEL-XAI>}
}
```

After the repository is archived with Zenodo, the final citation should be updated with the **real Zenodo DOI**.

---

## 16. License

This project is released under the MIT License. See [`LICENSE`](LICENSE) for details.

---

## Authors

- **Janani G** — Department of Computer Science, Vellore Institute of Technology, Vellore, India
- **Dr. D Deepa** — School of Computer Science and Engineering, Vellore Institute of Technology, Vellore, India
- **Aqsha Fathima I** — Department of Computer Science, Vellore Institute of Technology, Vellore, India
- **Gayathri M** — Department of Computer Science, Vellore Institute of Technology, Vellore, India
- **Rakshitha N** — Department of Computer Science, Vellore Institute of Technology, Vellore, India
- **Syed Fazila Musquan** — Department of Computer Science, Vellore Institute of Technology, Vellore, India
