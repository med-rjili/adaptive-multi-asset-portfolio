import numpy as np
import pytest
from adaptive_portfolio.strategies import STRATEGIES, allocate

def test_all_eight_strategies_long_only_and_budget():
    rng=np.random.default_rng(42)
    x=rng.normal(0.0003,.01,(530,8))
    for name in STRATEGIES:
        w=allocate(name,x)
        assert len(w)==8 and np.isfinite(w).all(),name
        assert np.all(w>=-1e-10),name
        assert abs(w.sum()-1)<1e-8,name

def test_unknown_strategy():
    with pytest.raises(ValueError): allocate("bad",np.ones((510,3))*.001)
