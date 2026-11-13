"""Eight long-only, fully invested allocation rules; no future returns used."""
import numpy as np
from scipy.optimize import minimize
from .risk import covariance, risk_contributions
from .regimes import regime_probability

STRATEGIES = ("equal_weight", "risk_parity", "minimum_variance", "maximum_sharpe", "momentum", "cvar", "regime_aware", "robust_mean_variance")

def simplex(x):
    x = np.maximum(np.asarray(x, float), 0)
    return x / x.sum() if x.sum() > 1e-12 else np.ones(len(x)) / len(x)

def _solve(fun, n, x0=None):
    x0 = np.ones(n)/n if x0 is None else simplex(x0)
    r = minimize(fun, x0, method="SLSQP", bounds=[(0,1)]*n,
                 constraints=[{"type":"eq","fun":lambda w: w.sum()-1}],
                 options={"maxiter":350, "ftol":1e-10})
    return simplex(r.x) if r.success and np.isfinite(r.fun) else x0

def allocate(name, history, rf=0.02):
    """history: past daily simple returns (up to and including decision close)."""
    x = np.asarray(history, float)
    n = x.shape[1]
    eq = np.ones(n)/n
    if name == "equal_weight": return eq
    cov = covariance(x)
    mu = np.mean(x,axis=0)*252
    if name == "risk_parity":
        def objective(w):
            rc = risk_contributions(w,cov)
            return np.sum((rc-rc.mean())**2)
        return _solve(objective,n)
    if name == "minimum_variance":
        return _solve(lambda w: w@cov@w,n)
    if name == "maximum_sharpe":
        # Shrink noisy mean toward cross-sectional average to temper overfitting.
        target = .5*mu + .5*mu.mean()
        return _solve(lambda w: -(w@(target-rf))/np.sqrt(max(w@cov@w,1e-12)),n)
    if name == "momentum":
        # 12-1 month cross-sectional momentum; long-only positive scores.
        if len(x)<252: return eq
        logret = np.log1p(x)
        score = np.expm1(logret[-252:-21].sum(axis=0))
        return simplex(np.maximum(score,0))
    if name == "cvar":
        losses = -x
        def objective(w):
            l=losses@w
            q=np.quantile(l,.95)
            return q+np.maximum(l-q,0).mean()/.05
        return _solve(objective,n)
    if name == "regime_aware":
        riskoff = regime_probability(x.mean(axis=1))
        low = _solve(lambda w: w@cov@w,n)
        # Momentum-tilted risk-on portfolio, without training on future returns.
        trend = np.expm1(np.log1p(x[-min(len(x),126):]).sum(axis=0))
        on = simplex(np.maximum(trend,0))
        return simplex(riskoff*low+(1-riskoff)*on)
    if name == "robust_mean_variance":
        # Ellipsoidal uncertainty in expected returns; diagonal covariance proxy.
        scale = np.sqrt(np.maximum(np.diag(cov),1e-12))
        mu_shrunk=.25*mu+.75*mu.mean()
        return _solve(lambda w: -w@mu_shrunk + 3*(w@cov@w)/2 + .15*np.linalg.norm(scale*w),n)
    raise ValueError(f"Unknown strategy: {name}")
