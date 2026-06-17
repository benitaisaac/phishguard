#!/usr/bin/env python3
"""Train the Logistic Regression model and export it to web/model.json.

The web dashboard re-implements feature extraction + inference in JavaScript and
loads these weights, so detection runs 100% client-side (no backend, no API keys).

Usage:  python scripts/export_model.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from phishguard import __version__
from phishguard.dataset import load_xy
from phishguard.features import FEATURE_NAMES
from phishguard.models import LogisticRegression


def main():
    X, y, _ = load_xy()
    model = LogisticRegression(epochs=600).fit(X, y)
    payload = {
        "version": __version__,
        "feature_names": FEATURE_NAMES,
        "weights": [round(w, 6) for w in model.w],
        "bias": round(model.b, 6),
        "means": [round(m, 6) for m in model.means],
        "stds": [round(s, 6) for s in model.stds],
        "trained_on": len(X),
    }
    out = os.path.join(os.path.dirname(__file__), "..", "web", "model.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Exported model ({len(FEATURE_NAMES)} features, trained on {len(X)} URLs) -> web/model.json")


if __name__ == "__main__":
    main()
