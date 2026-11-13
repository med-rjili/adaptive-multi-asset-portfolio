# Adaptive Multi-Asset Portfolio

**Eight quantitative investment strategies | Real ETF market data | Walk-forward research | Transaction costs | Reproducible Python**

> **Data integrity:** This project downloads real daily ETF closing prices from Stooq when executed with network access. No synthetic historical price data are presented as market observations. This repository does not claim any empirical outperformance until the data have been downloaded and the backtest executed. The published visualizations, if any, must be generated from a dated, provenance-documented real-price snapshot.

## Research question

Do adaptive allocations using market-regime probabilities and robust optimization outperform transparent allocations such as equal-weight and minimum variance, **out of sample and net of transaction costs**?

The objective is to provide an auditable research framework rather than an optimized performance claim. The comparison includes eight long-only fully invested strategies and controls for look-ahead leakage through a walk-forward decision schedule.

## Universe and data

| Ticker | Asset class |
|---|---|
| SPY | US large-cap equities |
| EFA | Developed ex-US equities |
| EEM | Emerging-market equities |
| IEF | US 7–10 year Treasury bonds |
| TLT | US long Treasury bonds |
| GLD | Gold |
| VNQ | US listed real estate |
| DBC | Broad commodities |

Source: [Stooq daily market data](https://stooq.com/). Prices are downloaded via `https://stooq.com/q/d/l/?s=spy.us&i=d`, and equivalents for the other tickers. Data are not checked into git; provider terms and the methodology of historical price adjustments must be verified independently. **Close-price backtests should not automatically be described as dividend-inclusive total-return backtests.** The sample begins at the first date all assets have observations. Historical ETF availability introduces survivorship/universe-selection limitations.

## Quickstart

```bash
python -m venv .venv
# Activate the virtual environment
pip install -e .
python scripts/download_data.py
python scripts/run_research.py --fee-bps 5 --window 504 --rebalance 21
pytest -q
```

The downloader requires internet access. If Stooq throttles requests or changes its API, the script fails with an explicit error instead of generating invented quotes. To use your own licensed daily close dataset, provide a CSV with `Date,SPY,EFA,EEM,IEF,TLT,GLD,VNQ,DBC` and run `python scripts/run_research.py --prices path/to/prices.csv`.

## Strategies and mathematics

Let $r_t\in\mathbb{R}^n$ be the vector of simple daily asset returns, $w_t\geq 0$ and $\mathbf 1^\top w_t=1$. All weights are estimated from the trailing $L=504$ returns, using the covariance estimator $\widehat\Sigma_t=252\,\widehat\Sigma_{\mathrm{LW}}$ (Ledoit–Wolf shrinkage), and recomputed every 21 sessions.

**1. Equal weight.** $w_i=1/n$. Serves as a transparent benchmark.

**2. Risk parity.** Minimize $\sum_i(RC_i-\overline{RC})^2$ where $RC_i=w_i(\Sigma w)_i/\sqrt{w^\top\Sigma w}$. Note that the optimizer uses absolute risk-contribution differences, not an exact closed-form parity solution.

**3. Minimum variance.** $\min_{w\in\Delta_n} w^\top\widehat\Sigma w$, where $\Delta_n=\{w\geq0,\mathbf1^\top w=1\}$.

**4. Maximum Sharpe.** $\max_{w\in\Delta_n}\frac{w^\top(\widetilde\mu-r_f\mathbf1)}{\sqrt{w^\top\widehat\Sigma w}}$. To temper noisy means, $\widetilde\mu=0.5\widehat\mu+0.5\overline\mu\mathbf1$, with $\widehat\mu=252\overline r$ and default $r_f=2\%$. The risk-free rate is a modeling assumption, not a fetched daily series.

**5. Momentum.** Cross-sectional positive 12–1 month momentum: $s_i=\prod_{j=t-251}^{t-21}(1+r_{j,i})-1$; weights are proportional to $\max(s_i,0)$. If all scores are non-positive, fall back to equal weight. This avoids using the most recent month for the momentum signal.

**6. CVaR.** Historical expected shortfall at $\alpha=0.95$:

```math
\min_{w\in\Delta_n,\eta}\left\lbrace \eta+\frac{1}{(1-\alpha)T}\sum_{j=1}^T\max(-w^\top r_j-\eta,0)\right\rbrace .
```

Implementation uses the Rockafellar–Uryasev **linear programming formulation** with nonnegative slack variables, solved using SciPy HiGHS.

**7. Regime-aware allocation.** Fit a two-component Gaussian mixture model to historical 21-day realized volatility of the equal-weight asset-return proxy. Order components by mean volatility; let $p_t$ be the posterior probability of the high-volatility component. Blend minimum-variance and positive six-month momentum allocations:

```math
w_t=p_t w_t^{\mathrm{minvar}}+(1-p_t)w_t^{\mathrm{trend}}.
```

**Important:** This is a *Gaussian mixture regime classifier*, **not an HMM**. It does not model Markov transition probabilities. All fitting occurs on the trailing historical window.

**8. Robust mean–variance.** Optimize a mean-shrunk, volatility-uncertainty-penalized objective:

```math
\min_{w\in\Delta_n}-\widetilde\mu^\top w+\frac{3}{2}w^\top\widehat\Sigma w+0.15\|\mathrm{diag}(\widehat\Sigma)^{1/2}w\|_2,
```

with $\widetilde\mu=0.25\widehat\mu+0.75\overline\mu\mathbf1$. The norm penalty can be interpreted as a simple ellipsoidal expected-return uncertainty set; the coefficients are *fixed ex ante*, not tuned on the test period.

## Walk-forward methodology

1. Calculate simple close-to-close returns without forward filling.
2. At decision close $t$, estimate weights using only returns up to and including $t$.
3. On rebalance dates, assume execution at close $t$; deduct $c\sum_i|w_{i,t}^{\mathrm{target}}-w_{i,t}^{\mathrm{pretrade}}|$, with $c=5$ basis points by default.
4. Earn the subsequent close-to-close portfolio return $w_t^\top r_{t+1}$.
5. Drift holdings after each return, and repeat the procedure. Compare cumulative wealth, CAGR, Sharpe, Sortino, Calmar, drawdowns, volatility, turnover and allocations.

**Execution caveat:** The closing-price fill assumption is idealized and not a realistic live execution guarantee. A production system should generate signals before the close or execute at next open with corresponding open prices and slippage. The default fee is per dollar traded; total absolute turnover counts buys and sells and should not be confused with half-turnover.

## Automated real-data figures on GitHub\n\nThe GitHub Actions workflow [Real-data research and figures](.github/workflows/research.yml) runs the unit tests, downloads a public **third-party mirror** of historical ETF dividend-adjusted closes, and then generates the backtest figures and CSV metrics. The workflow publishes generated figures and reports (but **not** the underlying price data) when it completes successfully. You can also start it manually from **Actions → Real-data research and figures → Run workflow**.\n\nThe mirror is described at [manisahni/marketdata](https://github.com/manisahni/marketdata) and is *not an exchange-verified feed*. The pipeline stores the original CSV SHA-256 and observation dates in `reports/data_provenance.json`. Stooq is still available through `python scripts/download_data.py`. Historical metrics are contingent on the availability and quality of the upstream provider. Do not treat vendor-adjusted close returns as executable fill prices.\n\n## Outputs

After running the research pipeline with real prices:

- `reports/performance_metrics.csv`: net-of-cost performance summary.
- `reports/equity_curves.csv`: cumulative wealth.
- `reports/portfolio_weights.csv`: weights at rebalance dates.
- `reports/turnover.csv`: turnover and cost by day and strategy.
- `figures/cumulative_wealth.png`: strategy comparison.
- `figures/drawdowns.png`: underwater curves.
- `figures/rolling_volatility.png`: realized rolling portfolio volatility.
- `figures/allocation_weights.png`: adaptive allocation history.
- `figures/turnover.png`: transaction-intensity comparison.

The five notebooks walk through data exploration, covariance estimation, allocation, regime classification and walk-forward evaluation.

## Validation and limitations

Unit tests check simplex constraints, cost drag, point-in-time invariance and input validation. Additional recommended work before using this as a trading model: next-open execution, bid/ask and market impact, actual dividend-adjusted total returns, dynamic funding rates, trading calendars, walk-forward hyperparameter selection, bootstrap confidence intervals, benchmark comparisons and sensitivity to data vendor. Gaussian mixture labels can be unstable; no claim of superior forecasting ability is made. This is **research software**, not investment advice.

## License

MIT. Data remain subject to their original provider terms.