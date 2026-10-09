"""Tests for feature extraction, models, and metrics."""

from __future__ import annotations

from phishguard.features import FEATURE_NAMES, extract, vectorize
from phishguard.metrics import cross_validate, metrics, roc_auc
from phishguard.models import GaussianNB, LinearSVM, LogisticRegression


# ---- features ----
def test_feature_vector_length_matches_names():
    assert len(vectorize("https://example.com")) == len(FEATURE_NAMES)


def test_https_and_ip_flags():
    assert extract("https://example.com")["uses_https"] == 1.0
    assert extract("http://example.com")["uses_https"] == 0.0
    assert extract("http://192.168.0.1/login")["has_ip"] == 1.0
    assert extract("https://example.com")["has_ip"] == 0.0


def test_suspicious_word_and_at_symbol():
    assert extract("http://secure-login-update.tk/verify")["has_suspicious_word"] == 1.0
    assert extract("http://good.com@evil.tk/")["has_at"] == 1.0
    assert extract("https://wikipedia.org")["has_suspicious_word"] == 0.0


def test_suspicious_tld_and_brand_subdomain():
    assert extract("http://x.tk")["suspicious_tld"] == 1.0
    assert extract("https://example.com")["suspicious_tld"] == 0.0
    assert extract("http://paypal.secure-login.tk/")["brand_in_subdomain"] == 1.0



# ---- models (toy, linearly separable) ----
def _toy():
    X = [[0, 0], [0, 1], [1, 0], [1, 1], [5, 5], [5, 6], [6, 5], [6, 6]]
    y = [0, 0, 0, 0, 1, 1, 1, 1]
    return X, y


def test_logreg_learns_toy():
    X, y = _toy()
    m = LogisticRegression(epochs=600).fit(X, y)
    assert m.predict(X) == y
    p = m.predict_proba([[6, 6]])[0]
    assert p > 0.5


def test_gnb_learns_toy():
    X, y = _toy()
    m = GaussianNB().fit(X, y)
    assert m.predict(X) == y


# ---- metrics ----
def test_metrics_perfect():
    mt = metrics([0, 1, 1, 0], [0, 1, 1, 0])
    assert mt["accuracy"] == 1.0 and mt["f1"] == 1.0


def test_metrics_values():
    mt = metrics([1, 1, 0, 0], [1, 0, 1, 0])  # tp1 fn1 fp1 tn1
    assert abs(mt["precision"] - 0.5) < 1e-9
    assert abs(mt["recall"] - 0.5) < 1e-9


def test_roc_auc_perfect_separation():
    assert roc_auc([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]) == 1.0


# ---- end-to-end on the real dataset ----
def test_pipeline_accuracy_is_high():
    from phishguard.dataset import load_xy
    X, y, _ = load_xy()
    res = cross_validate(LogisticRegression, X, y, k=5)
    assert res["accuracy"] > 0.9  # the engineered features should separate well

# ---- svm test -----

def test_svm_learns_toy():
    X, y = _toy()
    m = LinearSVM(epochs=1000).fit(X, y)
    assert m.predict(X) == y

    scores = m.decision_function([[6, 6]])
    assert scores[0] > 0

def test_svm_cross_validate():
    X, y = _toy()
    res = cross_validate(LinearSVM, X, y, k=4)

    assert res["accuracy"] > 0.9
    assert "auc" in res
    assert 0.0 <= res["auc"] <= 1.0
