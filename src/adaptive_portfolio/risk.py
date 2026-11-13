import numpy as np
from sklearn.covariance import LedoitWolf

def covariance(returns, shrink=True):
    x = np.asarray(returns, float)
    if shrink and x.shape[0] > 2:
        return LedoitWolf().fit(x).covariance_ * 252
    return np.cov(x, rowvar=False) * 252

def risk_contributions(weights, cov):
    w = np.asarray(weights)
    vol = np.sqrt(max(w @ cov @ w, 0))
    return w * (cov @ w) / vol if vol > 0 else np.zeros_like(w)
