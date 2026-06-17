# Architecture

PhishGuard has two coordinated halves that share **one model and one feature definition**:

```
                         ┌──────────────────────────┐
                         │   data/urls.csv (labels)  │
                         └────────────┬─────────────┘
                                      │  scripts/make_dataset.py (reproducible)
                ┌─────────────────────┴───────────────────────┐
                │                  Python core                  │
                │  features.py ─► models.py ─► metrics.py       │
                │       │             │            │            │
                │   (18 feats)   LogReg/GNB   CV + AUC          │
                │       └────────► explain.py (XAI)             │
                │  cli.py  ──  python -m phishguard <url>       │
                └───────────────────────┬──────────────────────┘
                                        │  scripts/export_model.py
                                        ▼
                              web/model.json (weights)
                                        │  loaded by
                                        ▼
                ┌──────────────────────────────────────────────┐
                │            Web dashboard (web/)               │
                │  app.js: feature port + sigmoid inference     │
                │  → verdict + gauge + explanation (XAI)        │
                │  100% client-side, dark/light, a11y, states   │
                └──────────────────────────────────────────────┘
```

## Why this design

- **Single source of truth for features.** `src/phishguard/features.py` defines the 18
  features; `web/assets/js/app.js` is a faithful 1:1 port. Outputs are verified to match
  to 4 decimal places, so the browser produces the same probabilities as the CLI.
- **Train once, run anywhere.** The model is trained in Python and exported to
  `web/model.json`; the dashboard does pure inference (no training in the browser).
- **No backend.** Inference is a dot product + sigmoid, so the dashboard is a static site
  with no server, no API keys, and no data leaving the device.

## Module responsibilities

| Module | Responsibility |
|--------|----------------|
| `features.py` | URL → 18-dim interpretable feature vector |
| `models.py` | `LogisticRegression`, `GaussianNB` (from scratch) |
| `metrics.py` | confusion matrix, accuracy/precision/recall/F1, ROC-AUC, k-fold CV |
| `explain.py` | per-prediction feature attributions |
| `dataset.py` | CSV → feature matrix |
| `cli.py` | command-line interface (`classify`, `--evaluate`) |
| `web/` | static dashboard (HTML/CSS/JS) doing client-side inference |

See [folder structure in the README](../README.md#-folder-structure) and the
[methodology](METHODOLOGY.md) for the math.
