"""
CAPM and factor model analysis for InvestorMate.
"""

from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from ..data.providers import get_data_provider
from ..data.constants import get_ticker_format
from ..utils.exceptions import DataFetchError, ValidationError


def _history_to_returns(ticker: str, period: str = "2y") -> pd.Series:
    """Daily simple returns from provider history."""
    data, _ = get_data_provider().get_history(
        ticker, period, "1d", auto_adjust=True, return_trace=False
    )
    if not data:
        raise DataFetchError(f"No history for {ticker}")
    df = pd.DataFrame.from_dict(data, orient="index")
    df.index = pd.to_datetime(df.index, utc=True)
    df = df.sort_index()
    close_col = "Close" if "Close" in df.columns else df.columns[0]
    prices = df[close_col].astype(float)
    return prices.pct_change().dropna()


def _align_returns(
    stock_returns: pd.Series, bench_returns: pd.Series
) -> tuple[np.ndarray, np.ndarray]:
    aligned = pd.concat([stock_returns, bench_returns], axis=1, join="inner").dropna()
    if len(aligned) < 30:
        raise DataFetchError("Insufficient overlapping return history for regression")
    return aligned.iloc[:, 0].values, aligned.iloc[:, 1].values


def capm_regression(
    ticker: str,
    benchmark: str = "SPY",
    *,
    period: str = "2y",
    risk_free_rate: float = 0.0,
) -> Dict[str, Any]:
    """
    CAPM regression: R_i - R_f = alpha + beta * (R_m - R_f).
    """
    stock_r = _history_to_returns(ticker, period)
    bench_r = _history_to_returns(benchmark, period)
    ri, rm = _align_returns(stock_r, bench_r)
    excess_i = ri - risk_free_rate / 252
    excess_m = rm - risk_free_rate / 252

    # OLS: excess_i = alpha + beta * excess_m
    X = np.column_stack([np.ones(len(excess_m)), excess_m])
    coeffs, residuals, rank, s = np.linalg.lstsq(X, excess_i, rcond=None)
    alpha_daily, beta = float(coeffs[0]), float(coeffs[1])

    fitted = alpha_daily + beta * excess_m
    ss_res = np.sum((excess_i - fitted) ** 2)
    ss_tot = np.sum((excess_i - np.mean(excess_i)) ** 2)
    r_squared = float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0

    # Annualize alpha (trading days)
    alpha_annual = alpha_daily * 252

    return {
        "ticker": ticker.upper(),
        "benchmark": benchmark.upper(),
        "beta": beta,
        "alpha_daily": alpha_daily,
        "alpha_annual": alpha_annual,
        "r_squared": r_squared,
        "observations": len(ri),
        "risk_free_rate": risk_free_rate,
    }


def jensen_alpha(
    ticker: str,
    benchmark: str = "SPY",
    *,
    period: str = "2y",
    risk_free_rate: float = 0.0,
) -> Dict[str, Any]:
    """
    Jensen's alpha: actual return minus CAPM expected return.
    """
    result = capm_regression(
        ticker, benchmark, period=period, risk_free_rate=risk_free_rate
    )
    stock_r = _history_to_returns(ticker, period)
    bench_r = _history_to_returns(benchmark, period)
    ri, rm = _align_returns(stock_r, bench_r)
    actual_annual = float(np.mean(ri) * 252)
    expected_annual = risk_free_rate + result["beta"] * (
        float(np.mean(rm) * 252) - risk_free_rate
    )
    j_alpha = actual_annual - expected_annual
    return {
        **result,
        "actual_return_annual": actual_annual,
        "expected_return_annual": expected_annual,
        "jensen_alpha": j_alpha,
    }


def risk_decomposition(
    ticker: str,
    benchmark: str = "SPY",
    *,
    period: str = "2y",
) -> Dict[str, Any]:
    """
    Decompose total variance into systematic and idiosyncratic components.
    """
    result = capm_regression(ticker, benchmark, period=period)
    stock_r = _history_to_returns(ticker, period)
    bench_r = _history_to_returns(benchmark, period)
    ri, rm = _align_returns(stock_r, bench_r)
    total_var = float(np.var(ri, ddof=1))
    systematic_var = float((result["beta"] ** 2) * np.var(rm, ddof=1))
    idiosyncratic_var = max(0.0, total_var - systematic_var)
    return {
        "ticker": ticker.upper(),
        "benchmark": benchmark.upper(),
        "beta": result["beta"],
        "total_variance": total_var,
        "systematic_variance": systematic_var,
        "idiosyncratic_variance": idiosyncratic_var,
        "systematic_pct": systematic_var / total_var if total_var else None,
        "idiosyncratic_pct": idiosyncratic_var / total_var if total_var else None,
    }


def factor_model(
    ticker: str,
    factor_returns: pd.DataFrame,
    *,
    period: str = "2y",
    model: str = "ff3",
) -> Dict[str, Any]:
    """
    Multi-factor regression using user-supplied factor returns.

    ``factor_returns`` must have a DatetimeIndex and columns such as
    ``Mkt-RF``, ``SMB``, ``HML`` (FF3) or additionally ``RMW``, ``CMA`` (FF5).
    Stock excess returns are regressed on the factor columns.
    """
    if factor_returns is None or factor_returns.empty:
        raise ValidationError("factor_returns DataFrame is required")

    stock_r = _history_to_returns(ticker, period)
    stock_r.index = (
        stock_r.index.tz_localize(None) if stock_r.index.tz else stock_r.index
    )
    factors = factor_returns.copy()
    factors.index = pd.to_datetime(factors.index)
    if factors.index.tz is not None:
        factors.index = factors.index.tz_localize(None)

    aligned = (
        pd.concat([stock_r.rename("stock")], axis=1).join(factors, how="inner").dropna()
    )
    if len(aligned) < 30:
        raise DataFetchError("Insufficient overlapping data for factor regression")

    y = aligned["stock"].values
    X_cols = [c for c in factors.columns if c in aligned.columns]
    if model == "ff3":
        X_cols = [c for c in ["Mkt-RF", "SMB", "HML"] if c in X_cols] or X_cols[:3]
    elif model == "ff5":
        X_cols = [
            c for c in ["Mkt-RF", "SMB", "HML", "RMW", "CMA"] if c in X_cols
        ] or X_cols

    X = np.column_stack([np.ones(len(aligned)), aligned[X_cols].values])
    coeffs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    alpha = float(coeffs[0])
    loadings = {col: float(coeffs[i + 1]) for i, col in enumerate(X_cols)}

    fitted = X @ coeffs
    ss_res = np.sum((y - fitted) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0

    return {
        "ticker": ticker.upper(),
        "model": model,
        "alpha_daily": alpha,
        "alpha_annual": alpha * 252,
        "factor_loadings": loadings,
        "r_squared": r_squared,
        "observations": len(aligned),
        "factors_used": X_cols,
    }


class CAPMAnalyzer:
    """CAPM and factor analysis bound to a single stock."""

    def __init__(self, ticker: str):
        self.ticker = ticker

    def capm(self, benchmark: str = "SPY", **kwargs) -> Dict[str, Any]:
        return capm_regression(self.ticker, benchmark, **kwargs)

    def jensen_alpha(self, benchmark: str = "SPY", **kwargs) -> Dict[str, Any]:
        return jensen_alpha(self.ticker, benchmark, **kwargs)

    def risk_decomposition(self, benchmark: str = "SPY", **kwargs) -> Dict[str, Any]:
        return risk_decomposition(self.ticker, benchmark, **kwargs)

    def factor_model(
        self, factor_returns: pd.DataFrame, model: str = "ff3", **kwargs
    ) -> Dict[str, Any]:
        return factor_model(self.ticker, factor_returns, model=model, **kwargs)
