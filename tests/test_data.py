import numpy as np
import pandas as pd
import pytest
from adaptive_portfolio.data import returns_from_prices, read_prices

def test_return_timing():
    prices=pd.DataFrame({"A":[100.,110.,99.]},index=pd.date_range("2025-01-01",periods=3))
    assert np.allclose(returns_from_prices(prices).A.values,[.1,-.1])

def test_invalid_prices(tmp_path):
    p=tmp_path/"bad.csv"
    p.write_text("Date,A\n2025-01-01,-1\n2025-01-02,2\n")
    with pytest.raises(ValueError): read_prices(p)
