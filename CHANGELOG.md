# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/) and this
project adheres to [Semantic Versioning](https://semver.org/).

## [1.1.0] — 2026-06-17

### Added
- **Web dashboard** (`web/`): premium, responsive, accessible UI with dark/light mode,
  loading/skeleton/empty/error states, and per-prediction explanations — runs 100%
  client-side by re-implementing the model in JavaScript.
- `scripts/export_model.py` — trains and exports the model to `web/model.json`.
- Professional footer with contact and social links.
- Community files: `CONTRIBUTING`, `CODE_OF_CONDUCT`, `SECURITY`, `CHANGELOG`, `.env.example`.
- GitHub issue/PR templates and additional CI (lint, Pages deploy, build verification).
- Documentation: `docs/ARCHITECTURE.md`, `docs/DEPLOYMENT.md`, screenshot.

### Changed
- Expanded README into a full open-source project page (overview, install, usage,
  configuration, deployment, contributing, FAQ, license).

### Notes
- All existing CLI/library functionality and tests are preserved (backward compatible).

## [1.0.0] — 2026-06-17

### Added
- Initial release: explainable phishing-URL detection in pure Python.
- 18 lexical/host URL features; Logistic Regression + Gaussian Naive Bayes from scratch.
- 5-fold cross-validation metrics, CLI (`phishguard`), tests, CI, and project report.
