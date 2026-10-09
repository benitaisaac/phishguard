"""Evaluation metrics and k-fold cross-validation (pure Python)."""

from __future__ import annotations

import random


def confusion(y_true, y_pred):
    tp = fp = tn = fn = 0
    for t, p in zip(y_true, y_pred):
        if t == 1 and p == 1: tp += 1
        elif t == 0 and p == 1: fp += 1
        elif t == 0 and p == 0: tn += 1
        else: fn += 1
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn}


def metrics(y_true, y_pred):
    c = confusion(y_true, y_pred)
    tp, fp, tn, fn = c["tp"], c["fp"], c["tn"], c["fn"]
    total = tp + fp + tn + fn
    acc = (tp + tn) / total if total else 0.0
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1, "confusion": c}


def roc_auc(y_true, scores):
    """Rank-based AUC (probability a random positive outranks a random negative)."""
    pos = [s for t, s in zip(y_true, scores) if t == 1]
    neg = [s for t, s in zip(y_true, scores) if t == 0]
    if not pos or not neg:
        return 0.5
    wins = ties = 0
    for sp in pos:
        for sn in neg:
            if sp > sn: wins += 1
            elif sp == sn: ties += 1
    return (wins + 0.5 * ties) / (len(pos) * len(neg))


def kfold_indices(n, k, seed=42):
    idx = list(range(n))
    random.Random(seed).shuffle(idx)
    folds = [idx[i::k] for i in range(k)]
    return folds


def cross_validate(model_factory, X, y, k=5, seed=42):
    """Return averaged metrics over k folds for a fresh model each fold."""
    folds = kfold_indices(len(X), k, seed)
    agg = {"accuracy": 0, "precision": 0, "recall": 0, "f1": 0, "auc": 0}

    for i in range(k):
        test_idx = set(folds[i])

        Xtr = [X[j] for j in range(len(X)) if j not in test_idx]
        ytr = [y[j] for j in range(len(X)) if j not in test_idx]

        Xte = [X[j] for j in folds[i]]
        yte = [y[j] for j in folds[i]]

        m = model_factory().fit(Xtr, ytr)

        pred = m.predict(Xte)

        if hasattr(m, "predict_proba"):
            scores = m.predict_proba(Xte)
        elif hasattr(m, "decision_function"):
            scores = m.decision_function(Xte)
        else:
            scores = pred

        mt = metrics(yte, pred)

        agg["accuracy"] += mt["accuracy"]
        agg["precision"] += mt["precision"]
        agg["recall"] += mt["recall"]
        agg["f1"] += mt["f1"]
        agg["auc"] += roc_auc(yte, scores)

    return {key: v / k for key, v in agg.items()}
