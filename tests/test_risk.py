"""Tests for RiskAnalyzer and Portfolio VaR / Monte Carlo."""

import numpy as np
import pandas as pd
import pytest

from investormate.analysis.risk import RiskAnalyzer, _norm_ppf


def test_norm_ppf_symmetric():
    assert abs(_norm_ppf(0.5)) < 1e-9
    z = _norm_ppf(0.975)
    assert z > 1.9


def test_var_historical():
    rng = np.random.default_rng(0)
    r = pd.Series(rng.normal(-0.0001, 0.01, 100))
    ra = RiskAnalyzer(r)
    v = ra.var_historical(0.95)
    assert v is not None
    assert v < r.quantile(0.5)


def test_var_parametric():
    rng = np.random.default_rng(1)
    r = pd.Series(rng.normal(0, 0.01, 200))
    ra = RiskAnalyzer(r)
    v = ra.var_parametric(0.95)
    assert v is not None
    assert v < 0


def test_monte_carlo_shape():
    rng = np.random.default_rng(2)
    r = pd.Series(rng.normal(0.0002, 0.01, 80))
    out = RiskAnalyzer(r).monte_carlo(100_000.0, n_simulations=500, horizon=20, random_seed=3)
    assert out["n_simulations"] == 500
    assert out["horizon_days"] == 20
    assert out["percentile_5"] < out["median_final"] < out["percentile_95"]


def test_monte_carlo_insufficient_raises():
    r = pd.Series(np.random.default_rng(4).normal(0, 0.01, 10))
    with pytest.raises(ValueError):
        RiskAnalyzer(r).monte_carlo(1.0, n_simulations=10, horizon=5)


def test_var_bad_confidence():
    r = pd.Series([0.01, -0.02, 0.0, 0.015, -0.01])
    with pytest.raises(ValueError):
        RiskAnalyzer(r).var_historical(1.2)
