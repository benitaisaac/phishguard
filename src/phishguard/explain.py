"""Explainability: why did the model flag (or clear) this URL?

For the logistic-regression model, each standardized feature's contribution to the
decision is weight * standardized_value. Ranking these gives a transparent,
per-prediction explanation — the 'explainable AI' contribution of this project.
"""

from __future__ import annotations

from .features import FEATURE_NAMES


def explain_logreg(model, x_raw, top=5):
    """Return the top contributing features for one raw feature vector."""
    xs = [(x_raw[j] - model.means[j]) / model.stds[j] for j in range(len(x_raw))]
    contribs = [(FEATURE_NAMES[j], model.w[j] * xs[j]) for j in range(len(xs))]
    contribs.sort(key=lambda kv: abs(kv[1]), reverse=True)
    return [
        {"feature": name, "contribution": round(val, 3),
         "direction": "→ phishing" if val > 0 else "→ legitimate"}
        for name, val in contribs[:top] if abs(val) > 1e-6
    ]
