"""
Portfolio class for InvestorMate.
Portfolio analysis and performance tracking.
"""

from typing import Dict, Optional

import numpy as np
import pandas as pd

from ..data.fetchers import get_yfinance_data, get_yfinance_stock_history


class Portfolio:
    """
    Portfolio tracker and analyzer.

    Example:
        >>> portfolio = Portfolio({"AAPL": 10, "GOOGL": 5})
        >>> print(portfolio.value)
        >>> print(portfolio.allocation)
    """

    def __init__(
        self,
        holdings: Dict[str, float],
        cost_basis: Optional[Dict[str, float]] = None,
    ):
        """
        Initialize portfolio.

        Args:
            holdings: Dictionary of {ticker: shares}
            cost_basis: Optional dictionary of {ticker: cost_per_share}
        """
        self.holdings = holdings
        self.cost_basis = cost_basis or {}
        self._cache = {}

    @property
    def value(self) -> float:
        """Get total portfolio value."""
        total = 0.0
        for ticker, shares in self.holdings.items():
            try:
                info = get_yfinance_data(ticker)
                price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
                total += price * shares
            except Exception:
                continue
        return total

    @property
    def allocation(self) -> Dict[str, float]:
        """Get allocation percentages by ticker."""
        total_value = self.value
        if total_value == 0:
            return {}

        allocations = {}
        for ticker, shares in self.holdings.items():
            try:
                info = get_yfinance_data(ticker)
                price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
                ticker_value = price * shares
                allocations[ticker] = (ticker_value / total_value) * 100
            except Exception:
                allocations[ticker] = 0.0

        return allocations

    @property
    def returns(self) -> Optional[float]:
        """Get total return % (requires cost_basis)."""
        if not self.cost_basis:
            return None

        total_cost = sum(
            self.cost_basis.get(ticker, 0) * shares
            for ticker, shares in self.holdings.items()
        )

        if total_cost == 0:
            return None

        current_value = self.value
        return ((current_value - total_cost) / total_cost) * 100

    def _get_portfolio_returns(self) -> Optional[pd.DataFrame]:
        """Get daily returns DataFrame for portfolio (per-ticker columns, aligned)."""
        if "returns_df" in self._cache:
            return self._cache["returns_df"]

        returns_data = {}

        for ticker in self.holdings.keys():
            try:
                history_dict = get_yfinance_stock_history(
                    ticker, period="6mo", interval="1d"
                )
                df = pd.DataFrame.from_dict(history_dict, orient="index")
                df.index = pd.to_datetime(df.index)

                # Calculate daily returns
                df["Returns"] = df["Close"].pct_change()
                returns_data[ticker] = df["Returns"]
            except Exception:
                continue

        if not returns_data:
            return None

        returns_df = pd.DataFrame(returns_data)
        returns_df = returns_df.dropna()

        self._cache["returns_df"] = returns_df
        return returns_df

    def _weighted_daily_returns(self) -> Optional[pd.Series]:
        """
        Value-weighted portfolio daily return series (6-month window).
        Uses current market value weights; renormalizes over tickers with data.
        """
        returns_df = self._get_portfolio_returns()
        if returns_df is None or len(returns_df) < 30:
            return None

        alloc = self.allocation
        if not alloc:
            return None

        cols = [c for c in returns_df.columns if c in alloc and alloc.get(c, 0) > 0]
        if not cols:
            return None

        w = np.array([alloc[c] / 100.0 for c in cols])
        w = w / w.sum()
        weighted = (returns_df[cols].values * w).sum(axis=1)
        return pd.Series(weighted, index=returns_df.index, name="portfolio")

    @property
    def sharpe_ratio(self) -> Optional[float]:
        """
        Calculate Sharpe ratio (simplified).
        Uses 6-month daily returns, value-weighted, assumes 0% risk-free rate.
        """
        try:
            portfolio_returns = self._weighted_daily_returns()
            if portfolio_returns is None or len(portfolio_returns) < 30:
                return None

            mean_return = portfolio_returns.mean()
            std_return = portfolio_returns.std()

            if std_return == 0:
                return None

            sharpe = (mean_return / std_return) * np.sqrt(252)
            return float(sharpe)
        except Exception:
            return None

    @property
    def sortino_ratio(self) -> Optional[float]:
        """
        Sortino ratio (annualized): excess return / downside deviation.
        Uses 0% minimum acceptable return; 6-month daily data.
        """
        try:
            pr = self._weighted_daily_returns()
            if pr is None or len(pr) < 30:
                return None
            downside = pr[pr < 0]
            if len(downside) < 5:
                return None
            down_std = downside.std()
            if down_std == 0:
                return None
            return float((pr.mean() / down_std) * np.sqrt(252))
        except Exception:
            return None

    @property
    def max_drawdown(self) -> Optional[float]:
        """
        Maximum peak-to-trough drawdown over the window (positive %).
        e.g. 25.0 means 25% drawdown from peak equity.
        """
        try:
            pr = self._weighted_daily_returns()
            if pr is None or len(pr) < 30:
                return None
            equity = (1 + pr).cumprod()
            peak = equity.cummax()
            dd = (equity - peak) / peak
            mdd = float(dd.min())
            return abs(mdd) * 100.0
        except Exception:
            return None

    @property
    def calmar_ratio(self) -> Optional[float]:
        """
        Calmar ratio: annualized return / max drawdown (as decimal).
        Uses mean daily return * 252 for annualized return estimate.
        """
        try:
            pr = self._weighted_daily_returns()
            if pr is None or len(pr) < 30:
                return None
            mdd_pct = self.max_drawdown
            if mdd_pct is None or mdd_pct == 0:
                return None
            ann_ret = float(pr.mean() * 252)
            mdd_dec = mdd_pct / 100.0
            return ann_ret / mdd_dec
        except Exception:
            return None

    def beta(self, benchmark: str = "SPY") -> Optional[float]:
        """
        Portfolio beta vs a benchmark (default SPY), from aligned daily returns.

        Args:
            benchmark: Ticker symbol for benchmark index/ETF.

        Returns:
            Beta or None if insufficient data.
        """
        try:
            pr = self._weighted_daily_returns()
            if pr is None or len(pr) < 30:
                return None
            history_dict = get_yfinance_stock_history(
                benchmark, period="6mo", interval="1d"
            )
            bdf = pd.DataFrame.from_dict(history_dict, orient="index")
            bdf.index = pd.to_datetime(bdf.index)
            br = bdf["Close"].pct_change()
            aligned = pd.concat([pr, br], axis=1, join="inner").dropna()
            aligned.columns = ["p", "b"]
            if len(aligned) < 30:
                return None
            cov = np.cov(aligned["p"], aligned["b"])
            var_b = np.var(aligned["b"], ddof=1)
            if var_b == 0:
                return None
            return float(cov[0, 1] / var_b)
        except Exception:
            return None

    def drawdown_series(self) -> Optional[pd.Series]:
        """
        Underwater plot series: drawdown from running peak at each date (-1 to 0).
        """
        try:
            pr = self._weighted_daily_returns()
            if pr is None or len(pr) < 2:
                return None
            equity = (1 + pr).cumprod()
            peak = equity.cummax()
            return (equity - peak) / peak
        except Exception:
            return None

    @property
    def volatility(self) -> Optional[float]:
        """Get annualized volatility (value-weighted)."""
        try:
            portfolio_returns = self._weighted_daily_returns()
            if portfolio_returns is None or len(portfolio_returns) < 30:
                return None

            daily_vol = portfolio_returns.std()

            # Annualize
            annual_vol = daily_vol * np.sqrt(252)
            return annual_vol * 100  # As percentage
        except Exception:
            return None

    @property
    def sector_allocation(self) -> Dict[str, float]:
        """Get allocation by sector."""
        sectors = {}
        total_value = self.value

        if total_value == 0:
            return {}

        for ticker, shares in self.holdings.items():
            try:
                info = get_yfinance_data(ticker)
                sector = info.get("sector", "Unknown")
                price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
                ticker_value = price * shares

                if sector in sectors:
                    sectors[sector] += ticker_value
                else:
                    sectors[sector] = ticker_value
            except Exception:
                continue

        # Convert to percentages
        return {
            sector: (value / total_value) * 100
            for sector, value in sectors.items()
        }

    @property
    def concentration(self) -> float:
        """
        Get portfolio concentration (Herfindahl index).
        0-100, where higher = more concentrated.
        """
        allocations = self.allocation
        if not allocations:
            return 0.0

        # Sum of squared weights
        concentration = sum((weight / 100) ** 2 for weight in allocations.values())
        return concentration * 100

    def add(self, ticker: str, shares: float, cost_per_share: Optional[float] = None):
        """
        Add position to portfolio.

        Args:
            ticker: Stock ticker
            shares: Number of shares
            cost_per_share: Cost basis per share (optional)
        """
        if ticker in self.holdings:
            self.holdings[ticker] += shares
        else:
            self.holdings[ticker] = shares

        if cost_per_share:
            self.cost_basis[ticker] = cost_per_share

        # Clear cache
        self._cache = {}

    def remove(self, ticker: str):
        """Remove position from portfolio."""
        if ticker in self.holdings:
            del self.holdings[ticker]
        if ticker in self.cost_basis:
            del self.cost_basis[ticker]

        # Clear cache
        self._cache = {}

    def __repr__(self) -> str:
        """String representation."""
        num_holdings = len(self.holdings)
        return f"Portfolio(holdings={num_holdings}, value=${self.value:,.2f})"
