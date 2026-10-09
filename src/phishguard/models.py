"""Machine-learning models implemented from scratch (pure Python, no numpy).

Implementing these by hand — rather than calling scikit-learn — makes the project
self-contained and demonstrates the underlying mathematics, which is the point of
a research/dissertation project.
"""

from __future__ import annotations

import math


def _standardize_fit(X):
    n, d = len(X), len(X[0])
    means = [0.0] * d
    for row in X:
        for j in range(d):
            means[j] += row[j]
    means = [m / n for m in means]
    stds = [0.0] * d
    for row in X:
        for j in range(d):
            stds[j] += (row[j] - means[j]) ** 2
    stds = [math.sqrt(s / n) or 1.0 for s in stds]
    return means, stds


def _standardize_apply(X, means, stds):
    return [[(row[j] - means[j]) / stds[j] for j in range(len(means))] for row in X]


def _sigmoid(z):
    if z < -35:
        return 0.0
    if z > 35:
        return 1.0
    return 1.0 / (1.0 + math.exp(-z))


class LogisticRegression:
    """Binary logistic regression trained by batch gradient descent."""

    name = "Logistic Regression"

    def __init__(self, lr=0.1, epochs=400, l2=0.0):
        self.lr, self.epochs, self.l2 = lr, epochs, l2
        self.w = None
        self.b = 0.0
        self.means = self.stds = None

    def fit(self, X, y):
        self.means, self.stds = _standardize_fit(X)
        Xs = _standardize_apply(X, self.means, self.stds)
        n, d = len(Xs), len(Xs[0])
        self.w = [0.0] * d
        self.b = 0.0
        for _ in range(self.epochs):
            gw = [0.0] * d
            gb = 0.0
            for i in range(n):
                z = self.b + sum(self.w[j] * Xs[i][j] for j in range(d))
                err = _sigmoid(z) - y[i]
                for j in range(d):
                    gw[j] += err * Xs[i][j]
                gb += err
            for j in range(d):
                self.w[j] -= self.lr * (gw[j] / n + self.l2 * self.w[j])
            self.b -= self.lr * gb / n
        return self

    def _proba_std(self, xs):
        z = self.b + sum(self.w[j] * xs[j] for j in range(len(xs)))
        return _sigmoid(z)

    def predict_proba(self, X):
        Xs = _standardize_apply(X, self.means, self.stds)
        return [self._proba_std(row) for row in Xs]

    def predict(self, X, threshold=0.5):
        return [1 if p >= threshold else 0 for p in self.predict_proba(X)]


class GaussianNB:
    """Gaussian Naive Bayes classifier."""

    name = "Gaussian Naive Bayes"

    def __init__(self):
        self.classes = [0, 1]
        self.priors = {}
        self.mean = {}
        self.var = {}

    def fit(self, X, y):
        d = len(X[0])
        for c in self.classes:
            rows = [X[i] for i in range(len(X)) if y[i] == c]
            self.priors[c] = len(rows) / len(X) if X else 0.5
            m = [sum(r[j] for r in rows) / len(rows) for j in range(d)]
            v = [sum((r[j] - m[j]) ** 2 for r in rows) / len(rows) + 1e-6 for j in range(d)]
            self.mean[c], self.var[c] = m, v
        return self

    def _log_likelihood(self, x, c):
        m, v = self.mean[c], self.var[c]
        ll = math.log(self.priors[c] + 1e-12)
        for j in range(len(x)):
            ll += -0.5 * math.log(2 * math.pi * v[j]) - ((x[j] - m[j]) ** 2) / (2 * v[j])
        return ll

    def predict_proba(self, X):
        out = []
        for x in X:
            l0, l1 = self._log_likelihood(x, 0), self._log_likelihood(x, 1)
            mx = max(l0, l1)
            e0, e1 = math.exp(l0 - mx), math.exp(l1 - mx)
            out.append(e1 / (e0 + e1))
        return out

    def predict(self, X, threshold=0.5):
        return [1 if p >= threshold else 0 for p in self.predict_proba(X)]

class LinearSVM:
    """Binary linear SVM trained with hinge-loss subgradient descent."""

    name = "Linear SVM"

    def __init__(self, lr=0.01, epochs=1000, lambda_param=0.01):
        self.lr = lr
        self.epochs = epochs
        self.lambda_param = lambda_param
        self.w = None
        self.b = 0.0
        self.means = self.stds = None

    def fit(self, X, y):
        self.means, self.stds = _standardize_fit(X)
        Xs = _standardize_apply(X, self.means, self.stds)

        n, d = len(Xs), len(Xs[0])
        self.w = [0.0] * d
        self.b = 0.0

        for _ in range(self.epochs):
            for i in range(n):
                yi = 1 if y[i] == 1 else -1

                score = self.b + sum(
                    self.w[j] * Xs[i][j] for j in range(d)
                )

                margin = yi * score

                if margin >= 1:
                    for j in range(d):
                        self.w[j] -= self.lr * (
                            2 * self.lambda_param * self.w[j]
                        )
                else:
                    for j in range(d):
                        self.w[j] -= self.lr * (
                            2 * self.lambda_param * self.w[j]
                            - yi * Xs[i][j]
                        )

                    self.b += self.lr * yi

        return self

    def decision_function(self, X):
        Xs = _standardize_apply(X, self.means, self.stds)

        return [
            self.b + sum(
                self.w[j] * row[j] for j in range(len(row))
            )
            for row in Xs
        ]

    def predict(self, X):
        return [
            1 if score >= 0 else 0
            for score in self.decision_function(X)
        ]
