import numpy as np
import pandas as pd
from adaptive_portfolio.backtest import run_backtest

def test_costs_lower_wealth():
    rng=np.random.default_rng(4)
    r=pd.DataFrame(rng.normal(.0002,.01,(280,3)),index=pd.bdate_range("2023-01-02",periods=280),columns=list("ABC"))
    free,_,_=run_backtest(r,window=126,rebalance=21,fee_bps=0,strategies=("equal_weight",))
    costly,_,_=run_backtest(r,window=126,rebalance=21,fee_bps=30,strategies=("equal_weight",))
    assert costly.iloc[-1,0]<free.iloc[-1,0]
    assert len(free)==153

def test_no_future_leakage():
    rng=np.random.default_rng(7)
    r=pd.DataFrame(rng.normal(0,.01,(180,3)),index=pd.bdate_range("2022-01-03",periods=180),columns=list("ABC"))
    e1,_,_=run_backtest(r,window=126,rebalance=21,strategies=("minimum_variance",))
    r.iloc[-1]=[.5,-.5,.1]
    e2,_,_=run_backtest(r,window=126,rebalance=21,strategies=("minimum_variance",))
    pd.testing.assert_frame_equal(e1.iloc[:-1],e2.iloc[:-1])
