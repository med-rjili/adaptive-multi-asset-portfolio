import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def create_figures(equity, weights, turnover, out="figures"):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    def save(name):
        plt.tight_layout();plt.savefig(out/name,dpi=165,bbox_inches="tight");plt.close()
    equity.plot(figsize=(12,6),lw=1.6,title="Walk-forward wealth (net of transaction costs)")
    plt.ylabel("Wealth, initial capital = 1");save("cumulative_wealth.png")
    (equity/equity.cummax()-1).plot(figsize=(12,5),title="Underwater drawdowns")
    plt.ylabel("Drawdown");save("drawdowns.png")
    (equity.pct_change().rolling(63).std()*np.sqrt(252)).plot(figsize=(12,5),title="Rolling 63-session annualized volatility")
    plt.ylabel("Annualized volatility");save("rolling_volatility.png")
    if not weights.empty:
        name="regime_aware" if "regime_aware" in weights.index.get_level_values(1) else weights.index.get_level_values(1)[0]
        w=weights.xs(name,level="strategy")
        w.plot.area(figsize=(12,5),title=f"Allocation at rebalances: {name}",ylim=(0,1))
        plt.ylabel("Portfolio weight");save("allocation_weights.png")
    turnover.groupby(level="strategy").turnover.sum().sort_values().plot.bar(figsize=(10,4),title="Total one-way plus sell turnover")
    plt.ylabel("Sum of absolute weight changes");save("turnover.png")
