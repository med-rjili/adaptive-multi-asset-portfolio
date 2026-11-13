"""Regression checks for reproducible research conventions."""
import numpy as np
import pandas as pd
from adaptive_portfolio.strategies import allocate, STRATEGIES
from adaptive_portfolio.backtest import run_backtest

def test_all_strategies_are_causal():
    rng = np.random.default_rng(123)
    hist = rng.normal(0.0003, 0.01, (530, 8))
    for name in STRATEGIES:
        first = allocate(name, hist)
        extended = np.vstack([hist, rng.normal(0, 0.05, (10, 8))])
        assert np.allclose(first, allocate(name, extended[:530])), name

def test_rebalancing_and_turnover_have_matching_dates():
    rng = np.random.default_rng(12)
    returns = pd.DataFrame(rng.normal(0.0002, .008, (300, 3)),
                           index=pd.bdate_range("2020-01-01", periods=300),
                           columns=list("ABC"))
    eq, weights, turnover = run_backtest(
        returns, window=126, rebalance=21, strategies=("equal_weight",))
    assert len(eq) == 173
    assert len(weights) == 9
    assert (turnover["turnover"] >= 0).all()
    assert (weights.sum(axis=1) - 1).abs().max() < 1e-10

def test_summary_metrics_include_first_realized_return():
    from adaptive_portfolio.metrics import summary
    eq = pd.DataFrame({"constant": [1.01, 1.01 * 1.02, 1.01 * 1.02 * 0.99]})
    result = summary(eq)
    expected = eq.iloc[-1, 0] ** (252 / 3) - 1
    assert np.isclose(result.loc["constant", "CAGR"], expected)
    assert np.isfinite(result.loc["constant", "volatility"])
