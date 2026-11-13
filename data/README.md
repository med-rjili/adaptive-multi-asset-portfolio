# Market data

Run `python scripts/download_data.py` to download actual ETF daily closing prices from Stooq into `data/prices_stooq.csv`.

The CSV is intentionally not committed. The downloader does not substitute synthetic data when a provider request fails.

For your own dataset, provide columns `Date,SPY,EFA,EEM,IEF,TLT,GLD,VNQ,DBC` and pass `--prices path/to/file.csv` to `scripts/run_research.py`.

Data provider terms, adjustment conventions and ETF inception dates should be verified before drawing investment conclusions.
