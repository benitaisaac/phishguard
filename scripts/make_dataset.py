#!/usr/bin/env python3
"""Generate a reproducible, labelled URL dataset (legitimate vs phishing).

This produces a *realistic synthetic* dataset so the project runs fully offline.
For a real evaluation, replace data/urls.csv with a public corpus such as
PhishTank or the Kaggle "Malicious URLs" dataset (same two columns: url,label).

Usage:  python scripts/make_dataset.py [n_per_class]
"""

from __future__ import annotations

import csv
import os
import random
import sys

SEED = 42

LEGIT_DOMAINS = [
    "google.com", "youtube.com", "facebook.com", "wikipedia.org", "amazon.com",
    "github.com", "stackoverflow.com", "microsoft.com", "apple.com", "netflix.com",
    "linkedin.com", "reddit.com", "instagram.com", "twitter.com", "paypal.com",
    "dropbox.com", "spotify.com", "adobe.com", "cloudflare.com", "mozilla.org",
    "python.org", "nytimes.com", "bbc.co.uk", "gov.in", "nic.in", "irctc.co.in",
    "flipkart.com", "zomato.com", "swiggy.com", "hdfcbank.com", "sbi.co.in",
]
LEGIT_PATHS = [
    "", "/", "/about", "/help/articles/123", "/search?q=books", "/user/profile",
    "/products/electronics", "/blog/2026/01/post", "/login", "/account/settings",
    "/watch?v=dQw4w9", "/docs/getting-started", "/contact-us", "/careers",
]
BRANDS = ["paypal", "apple", "microsoft", "amazon", "netflix", "hdfc", "sbi",
          "icici", "facebook", "instagram", "google", "amazon-pay", "irctc"]
SUSPICIOUS_WORDS = ["login", "verify", "secure", "account", "update", "confirm",
                    "signin", "banking", "webscr", "password", "billing", "alert"]
BAD_TLDS = ["tk", "ml", "ga", "cf", "gq", "xyz", "top", "club", "online", "info"]
RANDOM_HOST_WORDS = ["service", "center", "support", "portal", "auth", "user",
                     "client", "online", "official", "team", "id", "web"]


def rand_ip():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))


def gen_legit():
    dom = random.choice(LEGIT_DOMAINS)
    sub = random.choice(["", "", "", "www.", "mail.", "shop.", "blog."])
    path = random.choice(LEGIT_PATHS)
    return f"https://{sub}{dom}{path}"


def gen_phish():
    style = random.randint(0, 5)
    brand = random.choice(BRANDS)
    word = random.choice(SUSPICIOUS_WORDS)
    if style == 0:  # IP-based
        return f"http://{rand_ip()}/{brand}/{word}.php"
    if style == 1:  # brand as subdomain of junk domain
        junk = random.choice(RANDOM_HOST_WORDS) + str(random.randint(1, 999))
        tld = random.choice(BAD_TLDS)
        return f"http://{brand}.{word}-{junk}.{tld}/{word}"
    if style == 2:  # hyphen/digit heavy + suspicious word
        h = f"{brand}-{word}-{random.randint(1000,9999)}-secure"
        tld = random.choice(BAD_TLDS + ["com"])
        return f"http://{h}.{tld}/account/verify?id={random.randint(10000,99999)}"
    if style == 3:  # @ symbol trick
        return f"http://{random.choice(LEGIT_DOMAINS)}@{brand}-{word}.{random.choice(BAD_TLDS)}/"
    if style == 4:  # long random host
        h = "".join(random.choice("abcdef0123456789") for _ in range(18))
        return f"http://{word}.{h}.{random.choice(BAD_TLDS)}/{brand}/login.html"
    # style 5: deep subdomains imitating brand
    return (f"http://{word}.{brand}.com.{random.choice(RANDOM_HOST_WORDS)}"
            f".{random.choice(BAD_TLDS)}/update?account={brand}")


def main():
    random.seed(SEED)
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    rows = [("url", "label")]
    seen = set()
    for gen, label in ((gen_legit, 0), (gen_phish, 1)):
        made = 0
        while made < n:
            u = gen()
            if u in seen:
                continue
            seen.add(u)
            rows.append((u, label))
            made += 1
    random.shuffle(rows[1:])
    out = os.path.join(os.path.dirname(__file__), "..", "data", "urls.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
    print(f"Wrote {len(rows) - 1} rows ({n} per class) to data/urls.csv")


if __name__ == "__main__":
    main()
