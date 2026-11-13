"""Walk-forward, close-to-next-close returns; explicit execution convention.

At decision close t, compute weights from returns through t. Trade at close t
(idealized execution) and earn return t->t+1. This does not use future prices
in signal generation, but assumes closing prices are executable; live trading
would need next-open execution and open data. Trading costs deducted at t.
"""
import numpy as np
import pandas as pd
from .strategies import STRATEGIES, allocate

def run_backtest(returns, window=504, rebalance=21, fee_bps=5, rf=.02, strategies=STRATEGIES):
    if len(returns)<=window+2: raise ValueError("Insufficient history")
    if returns.isna().any().any(): raise ValueError("Missing returns")
    names=list(strategies)
    n=len(returns.columns)
    nav={k:1.0 for k in names}
    prev={k:np.zeros(n) for k in names}
    wealth={k:[] for k in names}
    weight_rows=[]
    turnover_rows=[]
    idx=[]
    arr=returns.to_numpy()
    for t in range(window,len(returns)-1):
        date=returns.index[t+1]
        idx.append(date)
        decision=(t-window)%rebalance==0
        for name in names:
            current=prev[name]
            if decision:
                target=allocate(name,arr[t-window+1:t+1],rf=rf)
                turnover=np.abs(target-current).sum()
                current=target
                weight_rows.append({"date":date,"strategy":name,**dict(zip(returns.columns,target))})
            else:
                turnover=0.0
            gross=float(current@arr[t+1])
            net=gross-(fee_bps/10000)*turnover
            nav[name]*=(1+net)
            wealth[name].append(nav[name])
            turnover_rows.append({"date":date,"strategy":name,"turnover":turnover,"cost":(fee_bps/10000)*turnover})
            prev[name]=current*(1+arr[t+1])/(1+gross)
    equity=pd.DataFrame(wealth,index=pd.DatetimeIndex(idx,name="Date"))
    weights=pd.DataFrame(weight_rows).set_index(["date","strategy"])
    turnover=pd.DataFrame(turnover_rows).set_index(["date","strategy"])
    return equity,weights,turnover
