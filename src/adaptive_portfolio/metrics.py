import numpy as np
import pandas as pd

def summary(equity, rf=0.02):
    r=equity.pct_change().dropna()
    years=len(r)/252
    result=[]
    for name in equity:
        a=r[name]
        cagr=(equity[name].iloc[-1]/equity[name].iloc[0])**(1/max(years,1e-9))-1
        vol=a.std()*np.sqrt(252)
        dd=equity[name]/equity[name].cummax()-1
        down=np.minimum(a-rf/252,0)
        result.append({"strategy":name,"CAGR":cagr,"volatility":vol,
                       "Sharpe":(a.mean()*252-rf)/vol if vol>0 else np.nan,
                       "Sortino":(a.mean()*252-rf)/(np.sqrt(np.mean(down**2))*np.sqrt(252)) if np.mean(down**2)>0 else np.nan,
                       "max_drawdown":dd.min(),"Calmar":cagr/abs(dd.min()) if dd.min()<0 else np.nan})
    return pd.DataFrame(result).set_index("strategy")
