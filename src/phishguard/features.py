"""Lexical + host-based feature extraction from a URL. Pure stdlib.

These hand-crafted features are interpretable, which is what makes the model's
decisions explainable (see explain.py). No network calls — everything is derived
from the URL string itself, so detection is instant and privacy-preserving.
"""

from __future__ import annotations

import math
import re
from urllib.parse import urlparse

SUSPICIOUS_WORDS = ("login", "verify", "secure", "account", "update", "confirm",
                    "signin", "sign-in", "banking", "webscr", "password", "billing",
                    "alert", "suspend", "unlock", "validate", "wallet")
BAD_TLDS = ("tk", "ml", "ga", "cf", "gq", "xyz", "top", "club", "online", "info",
            "click", "work", "support", "zip", "country", "stream")
BRANDS = ("paypal", "apple", "microsoft", "amazon", "netflix", "google", "facebook",
          "instagram", "hdfc", "sbi", "icici", "irctc", "whatsapp", "flipkart")
IP_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")

# The canonical, ordered list of feature names this module produces.
FEATURE_NAMES = [
    "url_length", "host_length", "path_length", "num_dots", "num_hyphens",
    "num_digits_host", "digit_ratio_host", "num_subdomains", "num_query_params",
    "num_special", "has_ip", "has_at", "uses_https", "has_suspicious_word",
    "suspicious_tld", "brand_in_subdomain", "host_entropy", "double_slash_redirect",
]


def _entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def extract(url: str) -> dict[str, float]:
    """Return an ordered dict of features for a single URL."""
    raw = (url or "").strip()
    if "://" not in raw:
        raw = "http://" + raw
    p = urlparse(raw)
    host = p.hostname or ""
    path = p.path or ""
    query = p.query or ""

    host_no_port = host
    labels = host_no_port.split(".") if host_no_port else []
    registered = ".".join(labels[-2:]) if len(labels) >= 2 else host_no_port
    subdomain = ".".join(labels[:-2]) if len(labels) > 2 else ""
    digits_host = sum(c.isdigit() for c in host_no_port)
    tld = labels[-1].lower() if labels else ""

    f = {
        "url_length": float(len(raw)),
        "host_length": float(len(host_no_port)),
        "path_length": float(len(path)),
        "num_dots": float(host_no_port.count(".")),
        "num_hyphens": float(raw.count("-")),
        "num_digits_host": float(digits_host),
        "digit_ratio_host": digits_host / len(host_no_port) if host_no_port else 0.0,
        "num_subdomains": float(max(0, len(labels) - 2)),
        "num_query_params": float(len(query.split("&")) if query else 0),
        "num_special": float(sum(raw.count(c) for c in "@%=&?_~")),
        "has_ip": 1.0 if IP_RE.match(host_no_port) else 0.0,
        "has_at": 1.0 if "@" in raw else 0.0,
        "uses_https": 1.0 if p.scheme == "https" else 0.0,
        "has_suspicious_word": 1.0 if any(w in raw.lower() for w in SUSPICIOUS_WORDS) else 0.0,
        "suspicious_tld": 1.0 if tld in BAD_TLDS else 0.0,
        "brand_in_subdomain": 1.0 if any(b in subdomain.lower() and b not in registered.lower() for b in BRANDS) else 0.0,
        "host_entropy": _entropy(host_no_port),
        "double_slash_redirect": 1.0 if raw.rfind("//") > 7 else 0.0,
    }
    return f


def vectorize(url: str) -> list[float]:
    """Feature vector in canonical FEATURE_NAMES order."""
    f = extract(url)
    return [f[name] for name in FEATURE_NAMES]
