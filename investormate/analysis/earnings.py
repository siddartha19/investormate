"""
Earnings calendar, estimates, and surprise history from yfinance-backed data.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..data.providers import get_data_provider


class EarningsAnalyzer:
    """
    Earnings calendar, consensus estimates, EPS trends, and reported vs expected EPS.

    Data source: Yahoo Finance via yfinance (availability varies by symbol).
    """

    def __init__(self, ticker: str):
        self.ticker = ticker

    def calendar(self) -> Dict[str, Any]:
        """
        Earnings-related calendar fields plus next earnings timestamps from ``info``.

        Returns:
            Dict with ``calendar`` (normalized table from yfinance), and optional
            ``earnings_timestamp``, ``earnings_call_timestamp`` from quote summary.
        """
        provider = get_data_provider()
        info = provider.get_info(self.ticker)
        return {
            "ticker": self.ticker,
            "calendar": provider.get_calendar(self.ticker),
            "earnings_timestamp": info.get("earningsTimestamp"),
            "earnings_call_timestamp": info.get("earningsCallTimestampStart"),
            "earnings_call_timestamp_end": info.get("earningsCallTimestampEnd"),
        }

    def surprise_history(self) -> List[Dict[str, Any]]:
        """
        Historical periods with EPS actual vs estimate and surprise % when available.

        Returns:
            List of dicts (one per row in yfinance ``earnings_history``), sorted by period key.
        """
        raw = get_data_provider().get_earnings_history(self.ticker)
        if not raw:
            return []
        out: List[Dict[str, Any]] = []
        for period_key, row in raw.items():
            if not isinstance(row, dict):
                continue
            actual = row.get("epsActual")
            estimate = row.get("epsAverage") or row.get("epsEstimate")
            surprise_pct = row.get("surprisePercent")
            if (
                surprise_pct is None
                and actual is not None
                and estimate not in (None, 0)
            ):
                try:
                    surprise_pct = (
                        (float(actual) - float(estimate)) / abs(float(estimate)) * 100.0
                    )
                except (TypeError, ValueError, ZeroDivisionError):
                    surprise_pct = None
            out.append(
                {
                    "period": period_key,
                    "eps_actual": actual,
                    "eps_estimate": estimate,
                    "surprise_percent": surprise_pct,
                    "revenue_actual": row.get("revenueActual"),
                    "revenue_estimate": row.get("revenueAverage"),
                }
            )
        out.sort(key=lambda r: str(r.get("period", "")))
        return out

    def estimates(self) -> Dict[str, Any]:
        """
        Consensus earnings and revenue estimate tables from yfinance.

        Returns:
            Dict with ``earnings`` and ``revenue`` keys (each a table dict or None).
        """
        provider = get_data_provider()
        return {
            "ticker": self.ticker,
            "earnings": provider.get_earnings_estimate(self.ticker),
            "revenue": provider.get_revenue_estimate(self.ticker),
        }

    def eps_trend(self) -> Optional[Dict]:
        """EPS revision trend table (7d / 30d / 60d / 90d columns when present)."""
        return get_data_provider().get_eps_trend(self.ticker)

    def eps_revisions(self) -> Optional[Dict]:
        """EPS up/down revision counts when provided by yfinance."""
        return get_data_provider().get_eps_revisions(self.ticker)

    def growth_estimates(self) -> Optional[Dict]:
        """Growth estimates vs sector / industry when provided by yfinance."""
        return get_data_provider().get_growth_estimates(self.ticker)
