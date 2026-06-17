# PhishGuard: Explainable Machine-Learning Phishing-URL Detection
### MCA Final-Year Project Report (scaffold)

> Fill in the institute name, guide, roll number, and dates. This is a complete
> structure with drafted content you can expand into a 40–60 page report.

---

## Abstract

Phishing remains one of the most prevalent cyber-attacks, tricking users into
revealing credentials through deceptive URLs. This project presents **PhishGuard**, a
lightweight, explainable phishing-URL detection system built entirely in pure Python.
PhishGuard extracts eighteen interpretable lexical and host-based features from a URL
and classifies it using two machine-learning models — Logistic Regression and Gaussian
Naive Bayes — implemented from first principles. Unlike many ML security tools that act
as black boxes, PhishGuard provides a per-prediction explanation identifying the
features responsible for each verdict. The models are evaluated using 5-fold
cross-validation across accuracy, precision, recall, F1-score and ROC-AUC. The system
performs detection purely from the URL string, requiring no network lookups, which makes
it fast and privacy-preserving.

**Keywords:** phishing detection, machine learning, URL classification, explainable AI,
cybersecurity, feature engineering.

---

## Chapter 1 — Introduction

### 1.1 Background
Phishing is a social-engineering attack in which adversaries impersonate trusted
entities to steal sensitive information. The URL is often the first and most reliable
signal of a phishing attempt.

### 1.2 Problem statement
Blacklist-based filters fail against newly created ("zero-hour") phishing URLs. There is
a need for a fast, content-independent classifier that generalises to unseen URLs **and**
explains its decisions so analysts and users can trust them.

### 1.3 Objectives
1. Engineer an interpretable feature set extracted purely from the URL string.
2. Implement and compare ML classifiers from scratch.
3. Provide explainable, per-prediction outputs.
4. Deliver a reproducible, open-source, dependency-free system.

### 1.4 Scope
Binary classification (phishing vs legitimate) using lexical/host features. Out of scope:
page-content analysis, screenshots, and live blacklist integration (listed as future work).

---

## Chapter 2 — Literature Review

| Approach | Idea | Limitation |
|----------|------|-----------|
| Blacklists (Google Safe Browsing, PhishTank) | Maintain known-bad URLs | Miss zero-hour URLs |
| Lexical ML (Ma et al., 2009) | Features from URL string | Needs good feature design |
| Content/HTML features | Parse page DOM | Requires fetching the page (slow, risky) |
| Deep learning (CNN/LSTM on URLs) | Learn features automatically | Data-hungry, opaque |
| Explainable ML (LIME/SHAP) | Attribute predictions | Rarely applied to phishing tools |

PhishGuard positions itself in the **lexical-ML + explainability** space: high speed,
no page fetch, and transparent decisions. See [REFERENCES.md](REFERENCES.md).

---

## Chapter 3 — System Analysis & Design

### 3.1 Functional requirements
- Classify a single URL; output verdict, probability, and explanation.
- Train/evaluate models on a labelled dataset; report metrics.

### 3.2 Non-functional requirements
- Run offline, zero third-party dependencies, < 1s per prediction.

### 3.3 Architecture
```
URL ─► Feature Extraction (18 features) ─► Standardisation ─► Model ─► Probability
                                                                  └─► Explanation (XAI)
```

### 3.4 Modules
`features.py`, `models.py`, `metrics.py`, `explain.py`, `dataset.py`, `cli.py`
(see [METHODOLOGY.md](METHODOLOGY.md)).

---

## Chapter 4 — Methodology

### 4.1 Dataset
Bundled realistic synthetic dataset (balanced, generated reproducibly with seed 42).
For deployment, a public corpus (PhishTank / Kaggle Malicious-URLs) can be dropped in.

### 4.2 Feature engineering
Eighteen features: URL/host/path lengths, dot/hyphen/digit counts, subdomain depth,
presence of an IP host, `@` symbol, HTTPS usage, suspicious keywords, suspicious TLDs,
brand-in-subdomain spoofing, host character entropy, and a `//` redirect indicator.

### 4.3 Models
- **Logistic Regression** — batch gradient descent on standardised features.
- **Gaussian Naive Bayes** — class-conditional Gaussian likelihoods.

### 4.4 Evaluation protocol
5-fold cross-validation; metrics: accuracy, precision, recall, F1, ROC-AUC.

### 4.5 Explainability
For Logistic Regression, the contribution of feature *j* to a decision is
`wⱼ · zⱼ` (weight × standardised value). The top contributions are reported per URL.

---

## Chapter 5 — Implementation

Pure Python 3, standard library only. Console tool `phishguard`. Unit + end-to-end
tests, continuous integration on Linux & Windows across Python 3.9–3.13.

---

## Chapter 6 — Results & Discussion

5-fold cross-validation results (reproduce with `python -m phishguard --evaluate`):

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|-------|:--------:|:---------:|:------:|:--:|:-------:|
| Logistic Regression | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| Gaussian Naive Bayes | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

**Discussion / threats to validity.** The near-perfect scores reflect the *synthetic*
dataset, whose classes are highly separable by construction. They demonstrate that the
feature set and models are correct, **but they over-estimate real-world performance**.
On public datasets, comparable lexical models report ~92–97% accuracy. The honest
reporting of this limitation is itself part of good research practice.

---

## Chapter 7 — Conclusion & Future Work

PhishGuard shows that a small, interpretable feature set with from-scratch models can
detect phishing URLs accurately *and* explainably, with zero dependencies.

**Future work:** integrate a real public dataset; add tree-ensemble and deep models;
incorporate WHOIS/DNS age features; SHAP-based explanations; a browser-extension
front-end; and a continuously updated blacklist fallback.

---

## Appendix

- Source: <https://github.com/aashishbharti04/phishguard>
- Reproduce dataset: `python scripts/make_dataset.py`
- Run tests: `pytest`
