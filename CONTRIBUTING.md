# Contributing to PhishGuard

Thanks for your interest in improving PhishGuard! 🛡️ Contributions of all kinds are welcome.

## Development setup

```bash
git clone https://github.com/aashishbharti04/phishguard
cd phishguard
pip install -e ".[dev]"     # installs pytest
pytest -q                    # run the test suite
```

Run the tools:

```bash
python -m phishguard "http://example.com/login"   # classify a URL
python -m phishguard --evaluate                    # 5-fold CV comparison
python scripts/make_dataset.py                      # regenerate the dataset
python scripts/export_model.py                      # rebuild web/model.json
```

Run the web dashboard locally:

```bash
python -m http.server 8000 --directory web
# open http://localhost:8000
```

## Ground rules

- **Keep the core dependency-free** (standard library only) for the Python package.
- **Add a test** for any behavior change (`tests/`). Keep CI green (Linux + Windows, Py 3.9–3.13).
- If you change `features.py`, also update the JS port in `web/assets/js/app.js` and
  re-run `python scripts/export_model.py` so the dashboard stays in sync.
- Match the existing code style; keep functions small and readable.

## Pull requests

1. Fork and create a feature branch.
2. Make your change + tests; run `pytest -q`.
3. Open a PR using the template; describe the change and link any issue.

## Reporting issues

Use the issue templates (bug report / feature request). Include the command/URL and output.

By contributing you agree your work is licensed under the [MIT License](LICENSE).
