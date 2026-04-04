"""
Portfolio return risk analytics: historical / parametric VaR and Monte Carlo paths.
"""

from __future__ import annotations

from statistics import NormalDist
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd


def _norm_ppf(p: float) -> float:
    """Inverse CDF of standard normal at ``p`` in (0, 1)."""
    if p <= 0.0 or p >= 1.0:
        raise ValueError("p must be strictly between 0 and 1")
    return float(NormalDist().inv_cdf(p))


class RiskAnalyzer:
    """
    Value-at-Risk and Monte Carlo simulation from a daily return series.

    VaR is reported as a **loss** in the same units as daily returns (e.g. -0.02 means 2% one-day loss
    at the chosen confidence level for historical VaR).
    """

    def __init__(self, returns: pd.Series):
        self.returns = returns.dropna()

    def var_historical(self, confidence: float = 0.95) -> Optional[float]:
        """
        Historical VaR: empirical quantile of daily returns at ``(1 - confidence)``.

        Args:
            confidence: e.g. 0.95 for 95% VaR.

        Returns:
            Return at the left tail (typically negative), or None if insufficient data.
        """
        r = self.returns
        if len(r) < 5:
            return None
        if not 0 < confidence < 1:
            raise ValueError("confidence must be between 0 and 1")
        q = (1.0 - confidence) * 100.0
        return float(np.percentile(r, q))

    def var_parametric(self, confidence: float = 0.95) -> Optional[float]:
        """
        Parametric (Gaussian) daily VaR using sample mean and std of returns.

        Returns:
            ``mean + z * std`` where ``z`` is the standard normal quantile at ``1 - confidence``.
        """
        r = self.returns
        if len(r) < 5:
            return None
        if not 0 < confidence < 1:
            raise ValueError("confidence must be between 0 and 1")
        mu = float(r.mean())
        sigma = float(r.std())
        if sigma == 0:
            return None
        z = _norm_ppf(1.0 - confidence)
        return mu + z * sigma

    def monte_carlo(
        self,
        portfolio_value: float,
        n_simulations: int = 1000,
        horizon: int = 252,
        random_seed: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Bootstrap terminal portfolio value by sampling daily returns with replacement.

        Args:
            portfolio_value: Starting portfolio value (currency units).
            n_simulations: Number of paths.
            horizon: Trading days per path.
            random_seed: Optional RNG seed for reproducibility.

        Returns:
            Dict with mean/median/percentiles of simulated terminal values.
        """
        r = self.returns.values.astype(float)
        if len(r) < 30:
            raise ValueError("Need at least 30 return observations for Monte Carlo")
        if portfolio_value <= 0:
            raise ValueError("portfolio_value must be positive")
        rng = np.random.default_rng(random_seed)
        idx = rng.integers(0, len(r), size=(n_simulations, horizon))
        daily = r[idx]
        factors = np.prod(1.0 + daily, axis=1)
        sim_final = portfolio_value * factors
        return {
            "start_value": float(portfolio_value),
            "horizon_days": int(horizon),
            "n_simulations": int(n_simulations),
            "mean_final": float(np.mean(sim_final)),
            "median_final": float(np.median(sim_final)),
            "percentile_5": float(np.percentile(sim_final, 5)),
            "percentile_95": float(np.percentile(sim_final, 95)),
        }
