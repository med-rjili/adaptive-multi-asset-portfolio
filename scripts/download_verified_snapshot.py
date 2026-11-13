"""Fetch a publicly accessible, third-party adjusted-close snapshot.

The mirror is not an official exchange feed. Independently verify provider
provenance and redistribution rights before use in production.
No synthetic fallback. The original price matrix is not committed to Git.
"""
from io import StringIO
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone
import requests
import pandas as pd

URL = "https://raw.githubusercontent.com/manisahni/marketdata/main/daily_adjclose.csv"
TICKERS = ("SPY", "EFA", "EEM", "IEF", "TLT", "GLD", "VNQ", "DBC")

def main():
    response = requests.get(URL, timeout=90, headers={"User-Agent": "AcademicPortfolioResearch/1.0"})
    response.raise_for_status()
    raw = response.content
    prices = pd.read_csv(StringIO(raw.decode("utf-8")), index_col="Date", parse_dates=True)
    if not set(TICKERS).issubset(prices.columns):
        raise ValueError("Missing required ETF symbols in upstream snapshot")
    if not prices.index.is_unique or not prices.index.is_monotonic_increasing:
        raise ValueError("Dates must be unique and sorted")
    prices = prices.loc[:, list(TICKERS)].dropna(how="any")
    if len(prices) < 1000 or not (prices > 0).all().all():
        raise ValueError("Invalid or insufficient historical ETF data")
    if not prices.index.min() < pd.Timestamp("2010-01-01"):
        raise ValueError("Snapshot has unexpectedly short history")
    dest = Path("data/prices_stooq.csv")
    dest.parent.mkdir(parents=True, exist_ok=True)
    prices.to_csv(dest, index_label="Date")
    report = Path("reports")
    report.mkdir(exist_ok=True)
    metadata = {
        "source_url": URL,
        "source_type": "third-party public mirror of yfinance adjusted closes",
        "sha256_original_csv": hashlib.sha256(raw).hexdigest(),
        "downloaded_utc": datetime.now(timezone.utc).isoformat(),
        "first_common_date": str(prices.index.min().date()),
        "last_common_date": str(prices.index.max().date()),
        "observations": len(prices),
        "tickers": list(TICKERS),
        "caveats": [
            "Third-party dataset; not independently verified against an exchange feed.",
            "Adjusted closes as described by upstream; not an executable trading price.",
            "Survivorship, vendor revisions, and close-execution assumptions apply."
        ]
    }
    (report / "data_provenance.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))

if __name__ == "__main__":
    main()
