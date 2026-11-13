"""Point-in-time Gaussian mixture regime probabilities; NOT a time-series HMM."""
import numpy as np
from sklearn.mixture import GaussianMixture

def regime_probability(history, seed=17):
    """Fit on trailing past market returns; estimate latest risk-off probability.

    Feature: trailing 21-day realized market volatility, using observations
    through previous close only. Regime label is ordered by fitted mean vol.
    """
    x = np.asarray(history, float)
    if len(x) < 126:
        return 0.5
    rolling = np.array([np.std(x[i-20:i+1], ddof=1)*np.sqrt(252) for i in range(20, len(x))])
    if np.std(rolling) < 1e-9:
        return 0.5
    model = GaussianMixture(n_components=2, covariance_type="full", random_state=seed, reg_covar=1e-5, n_init=2)
    model.fit(rolling.reshape(-1,1))
    high = np.argmax(model.means_.ravel())
    return float(model.predict_proba(rolling[-1:].reshape(-1,1))[0, high])
