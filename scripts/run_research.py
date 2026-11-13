from pathlib import Path
import argparse
from adaptive_portfolio.data import read_prices, returns_from_prices
from adaptive_portfolio.backtest import run_backtest
from adaptive_portfolio.metrics import summary
from adaptive_portfolio.plots import create_figures

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--prices",default="data/prices_stooq.csv")
    parser.add_argument("--fee-bps",type=float,default=5.)
    parser.add_argument("--window",type=int,default=504)
    parser.add_argument("--rebalance",type=int,default=21)
    args=parser.parse_args()
    prices=read_prices(args.prices)
    equity,weights,turnover=run_backtest(returns_from_prices(prices),window=args.window,rebalance=args.rebalance,fee_bps=args.fee_bps)
    Path("reports").mkdir(exist_ok=True)
    equity.to_csv("reports/equity_curves.csv")
    weights.to_csv("reports/portfolio_weights.csv")
    turnover.to_csv("reports/turnover.csv")
    result=summary(equity)
    result.to_csv("reports/performance_metrics.csv")
    create_figures(equity,weights,turnover)
    print(result.round(3).to_string())
