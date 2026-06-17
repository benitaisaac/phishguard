# Methodology — the math behind PhishGuard

## 1. Feature representation
Each URL `u` is mapped to a vector **x** ∈ ℝ¹⁸ by `features.vectorize`. Features are
lexical (counts/lengths/ratios over the URL string) and host-based (IP, TLD, subdomain
spoofing, entropy). All are computed from the string — no network access.

**Host character entropy** (Shannon):
```
H(s) = - Σ p(c) · log2 p(c)
```
where `p(c)` is the frequency of character `c` in the hostname. High entropy often
indicates algorithmically generated / obfuscated hosts.

## 2. Standardisation
Features are standardised to zero mean and unit variance:
```
z_j = (x_j - μ_j) / σ_j
```
μ_j, σ_j are learned on the training fold only (no leakage).

## 3. Logistic Regression
Hypothesis:
```
p = σ(w·z + b),   σ(t) = 1 / (1 + e^(-t))
```
Trained by minimising the cross-entropy loss via batch gradient descent:
```
∂L/∂w_j = (1/n) Σ (σ(w·zᵢ+b) - yᵢ) · z_ij
w_j ← w_j - η · (∂L/∂w_j + λ·w_j)
```
(η = learning rate, λ = L2 regularisation, default 0).

## 4. Gaussian Naive Bayes
Assuming class-conditional feature independence with Gaussian likelihoods:
```
P(y=c | x) ∝ P(c) · Π_j N(x_j ; μ_{c,j}, σ²_{c,j})
```
Computed in log-space for numerical stability; the positive-class posterior is returned
via a softmax over the two class log-likelihoods.

## 5. Evaluation
- **Confusion matrix** → accuracy, precision, recall, F1.
- **ROC-AUC** via the rank statistic: the probability a random phishing URL is scored
  higher than a random legitimate one (Mann–Whitney U formulation).
- **k-fold cross-validation** (k=5): the data is shuffled (seeded) and split into k
  folds; each fold is held out once while a fresh model trains on the rest.

## 6. Explainability
For Logistic Regression, the signed contribution of feature j to a single prediction is
`c_j = w_j · z_j`. Ranking |c_j| yields the features that most pushed the decision toward
"phishing" (positive) or "legitimate" (negative). This is a faithful, model-intrinsic
explanation (no surrogate model required).
