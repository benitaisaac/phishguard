"""Command-line interface for PhishGuard."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .dataset import load_xy
from .explain import explain_logreg
from .features import vectorize
from .metrics import cross_validate
from .models import GaussianNB, LogisticRegression


def cmd_evaluate(args):
    X, y, _ = load_xy(args.data)
    print(f"Dataset: {len(X)} URLs, {sum(y)} phishing / {len(y) - sum(y)} legitimate\n")
    print("5-fold cross-validation (averaged):\n")
    header = f"{'Model':<24}{'Acc':>8}{'Prec':>8}{'Recall':>8}{'F1':>8}{'AUC':>8}"
    print(header); print("-" * len(header))
    for factory in (LogisticRegression, GaussianNB):
        m = cross_validate(factory, X, y, k=5)
        print(f"{factory().name:<24}{m['accuracy']:>8.3f}{m['precision']:>8.3f}"
              f"{m['recall']:>8.3f}{m['f1']:>8.3f}{m['auc']:>8.3f}")
    return 0


def cmd_classify(args):
    X, y, _ = load_xy(args.data)
    model = LogisticRegression().fit(X, y)
    xv = vectorize(args.url)
    prob = model.predict_proba([xv])[0]
    verdict = "PHISHING" if prob >= 0.5 else "LEGITIMATE"
    conf = prob if prob >= 0.5 else 1 - prob
    print(f"\n  URL:      {args.url}")
    print(f"  Verdict:  {verdict}")
    print(f"  Phishing probability: {prob:.1%}  (confidence {conf:.1%})\n")
    print("  Top contributing features:")
    for c in explain_logreg(model, xv, top=6):
        print(f"    {c['direction']:<14} {c['feature']:<22} {c['contribution']:+.3f}")
    print()
    return 0


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError, OSError):
        pass
    p = argparse.ArgumentParser(
        prog="phishguard",
        description="Explainable ML phishing-URL detector (pure Python).")
    p.add_argument("url", nargs="?", help="a URL to classify")
    p.add_argument("--evaluate", action="store_true", help="run 5-fold CV model comparison")
    p.add_argument("--data", help="path to a urls.csv (url,label)")
    p.add_argument("--version", action="version", version=f"phishguard {__version__}")
    args = p.parse_args(argv)

    if args.evaluate:
        return cmd_evaluate(args)
    if args.url:
        return cmd_classify(args)
    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
