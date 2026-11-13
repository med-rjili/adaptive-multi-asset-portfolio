"""Real daily ETF prices via Stooq; no synthetic market history."""
from io import StringIO
from pathlib import Path
import time
import pandas as pd
import requests

TICKERS = ("SPY", "EFA", "EEM", "IEF", "TLT", "GLD", "VNQ", "DBC")

def download_stooq(tickers=TICKERS, start="2010-01-01", end=None, cache="data/prices_stooq.csv"):
    """Download actual historical closes from Stooq. Requires network. Do not forward-fill missing prices."""
    cols = {}
    for symbol in tickers:
        url = "https://stooq.com/q/d/l/"
        params = {"s": f"{symbol.lower()}.us", "i": "d", "d1": start.replace("-", "")}
        if end:
            params["d2"] = end.replace("-", "")
        response = requests.get(url, params=params, timeout=30, headers={"User-Agent": "AcademicPortfolioResearch/0.1"})
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        if not {"Date", "Close"}.issubset(df):
            raise ValueError(f"No valid price history for {symbol}; Stooq response: {response.text[:100]}")
        series = df.assign(Date=pd.to_datetime(df.Date)).set_index("Date").sort_index().Close
        cols[symbol] = series
        time.sleep(.15)
    prices = pd.concat(cols, axis=1).sort_index().dropna(how="any")
    if len(prices) < 252:
        raise ValueError("Insufficient overlapping real price history (<252 sessions)")
    if cache:
        dest = Path(cache)
        dest.parent.mkdir(parents=True, exist_ok=True)
        prices.to_csv(dest, index_label="Date")
    return prices

def read_prices(path):
    prices = pd.read_csv(path, index_col="Date", parse_dates=True).sort_index()
    if not prices.index.is_unique or (prices <= 0).any().any():
        raise ValueError("Dates must be unique and prices positive")
    return prices.dropna(how="any")

def returns_from_prices(prices):
    return prices.pct_change(fill_method=None).dropna(how="any")
