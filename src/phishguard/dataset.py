"""Load the labelled URL dataset and turn it into feature vectors."""

from __future__ import annotations

import csv
import os

from .features import vectorize

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "urls.csv")


def load_raw(path: str | None = None):
    path = path or DATA_PATH
    urls, labels = [], []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            urls.append(row["url"])
            labels.append(int(row["label"]))
    return urls, labels


def load_xy(path: str | None = None):
    urls, labels = load_raw(path)
    X = [vectorize(u) for u in urls]
    return X, labels, urls
