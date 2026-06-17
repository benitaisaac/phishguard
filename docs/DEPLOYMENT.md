# Deployment Guide

PhishGuard has two deliverables: the **Python CLI/library** and the **static web dashboard**.

## 1. Web dashboard → GitHub Pages (recommended)

The repository ships a workflow ([`.github/workflows/pages.yml`](../.github/workflows/pages.yml))
that publishes the `web/` folder to GitHub Pages on every push to `main`.

**One-time setup:** repo **Settings → Pages → Source: GitHub Actions**. Then every push
deploys automatically to `https://<user>.github.io/phishguard/`.

If you change the model or features, regenerate the exported weights first:

```bash
python scripts/export_model.py    # rewrites web/model.json
git add web/model.json && git commit -m "chore: refresh model" && git push
```

### Any static host
The dashboard is plain static files. Deploy `web/` to Netlify, Vercel, Cloudflare Pages,
S3, or any web server — no build step required.

## 2. Web dashboard → run locally

```bash
python -m http.server 8000 --directory web
# open http://localhost:8000
```

## 3. Python package

```bash
pip install -e .            # editable install → `phishguard` command
phishguard "http://example.com/login"
phishguard --evaluate
```

To build distributable artifacts:

```bash
python -m build             # creates dist/*.whl and *.tar.gz
```

## CI / quality gates

- [`ci.yml`](../.github/workflows/ci.yml) — tests + CLI smoke on Linux & Windows, Py 3.9–3.13.
- [`lint.yml`](../.github/workflows/lint.yml) — Ruff lint + byte-compile check.
- [`pages.yml`](../.github/workflows/pages.yml) — deploy the dashboard.
