from adaptive_portfolio.data import download_stooq
if __name__=="__main__":
    prices=download_stooq()
    print(f"Downloaded {len(prices)} actual daily closes; {prices.index.min().date()} to {prices.index.max().date()}")
