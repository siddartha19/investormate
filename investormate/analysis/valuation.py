"""
Valuation module for InvestorMate.
DCF (Discounted Cash Flow), comparable companies, and fair value summary.
"""

from typing import Dict, List, Optional, Any

from ..utils.helpers import safe_divide
from ..data.fetchers import get_yfinance_data
from ..data.constants import get_ticker_format


class Valuation:
    """
    Stock valuation: DCF, comparable companies (comps), and fair value summary.

    Example:
        >>> stock = Stock("AAPL")
        >>> dcf = stock.valuation.dcf(growth_rate=0.05)
        >>> comps = stock.valuation.comps(peers=["MSFT", "GOOGL", "META"])
        >>> summary = stock.valuation.summary(peers=["MSFT", "GOOGL"])
    """

    def __init__(
        self,
        ticker: str,
        info: Optional[Dict] = None,
        ratios: Optional[Any] = None,
        balance_sheet: Optional[Dict] = None,
        income_stmt: Optional[Dict] = None,
        cash_flow: Optional[Dict] = None,
    ):
        """
        Initialize valuation for a stock.

        Args:
            ticker: Stock ticker symbol
            info: Stock info dict (from yfinance). Fetched if None.
            ratios: RatiosCalculator instance (for WACC). Optional.
            balance_sheet: Balance sheet dict. Optional.
            income_stmt: Income statement dict. Optional.
            cash_flow: Cash flow dict. Optional.
        """
        self.ticker = ticker
        if info is None:
            info = get_yfinance_data(get_ticker_format(ticker))
        self._info = info or {}
        self._ratios = ratios
        self._balance_sheet = balance_sheet or {}
        self._income_stmt = income_stmt or {}
        self._cash_flow = cash_flow or {}

    def _get_fcf(self) -> Optional[float]:
        """Get trailing free cash flow (FCF). Prefer info['freeCashflow'], else derive."""
        fcf = self._info.get("freeCashflow")
        if fcf is not None and fcf > 0:
            return float(fcf)
        # Fallback: operating cash flow - cap ex (from cash flow statement or info)
        ocf = self._info.get("operatingCashflow")
        cap_ex = self._info.get("capitalExpenditure") or self._info.get("capitalExpenditures")
        if cap_ex is not None:
            cap_ex = abs(float(cap_ex))
        if ocf is not None:
            return float(ocf) - (cap_ex or 0)
        return None

    def _get_shares(self) -> Optional[float]:
        """Get shares outstanding."""
        s = self._info.get("sharesOutstanding") or self._info.get("floatShares")
        return float(s) if s is not None else None

    def dcf(
        self,
        growth_rate: float = 0.05,
        terminal_growth: float = 0.02,
        years: int = 5,
        wacc: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Discounted Cash Flow (DCF) valuation with terminal value.

        Projects FCF for `years` at `growth_rate`, then applies terminal value
        using perpetuity growth at `terminal_growth`. Discounts to present value
        using WACC.

        Args:
            growth_rate: Annual FCF growth rate (e.g., 0.05 = 5%)
            terminal_growth: Terminal perpetual growth rate (e.g., 0.02 = 2%)
            years: Number of years to project (default 5)
            wacc: Discount rate. Uses stock's WACC from ratios if None.

        Returns:
            Dict with keys: fair_value_per_share, enterprise_value, dcf_value,
            terminal_value_pv, fcf_series, wacc_used, assumptions.
        """
        fcf0 = self._get_fcf()
        shares = self._get_shares()
        wacc_used = wacc
        if wacc_used is None and self._ratios is not None:
            wacc_used = self._ratios.wacc
        if wacc_used is None:
            wacc_used = 0.10  # fallback 10%

        result = {
            "fair_value_per_share": None,
            "enterprise_value": None,
            "dcf_value": None,
            "terminal_value_pv": None,
            "fcf_series": [],
            "wacc_used": wacc_used,
            "assumptions": {
                "growth_rate": growth_rate,
                "terminal_growth": terminal_growth,
                "years": years,
            },
        }

        if fcf0 is None or fcf0 <= 0 or shares is None or shares <= 0:
            return result

        # Project FCF
        fcf_series = []
        fcf = fcf0
        pv_fcf = 0.0
        for i in range(1, years + 1):
            fcf_series.append(round(fcf, 2))
            pv_fcf += fcf / ((1 + wacc_used) ** i)
            fcf = fcf * (1 + growth_rate)

        # Terminal value at end of year `years`: TV = FCF_n * (1 + g_term) / (WACC - g_term)
        fcf_last = fcf_series[-1]
        if wacc_used <= terminal_growth:
            terminal_value = 0.0
        else:
            terminal_value = fcf_last * (1 + terminal_growth) / (wacc_used - terminal_growth)
        terminal_value_pv = terminal_value / ((1 + wacc_used) ** years)

        enterprise_value = pv_fcf + terminal_value_pv
        fair_value_per_share = enterprise_value / shares

        result["dcf_value"] = round(pv_fcf, 2)
        result["terminal_value_pv"] = round(terminal_value_pv, 2)
        result["enterprise_value"] = round(enterprise_value, 2)
        result["fair_value_per_share"] = round(fair_value_per_share, 2)
        result["fcf_series"] = fcf_series
        return result

    def comps(
        self,
        peers: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Comparable companies (peer multiples) valuation.

        Fetches P/E, EV/EBITDA, and P/S for the stock and peers, then computes
        median peer multiples and implied value per share for this stock.

        Args:
            peers: List of peer tickers (e.g., ["MSFT", "GOOGL"]). Required.

        Returns:
            Dict with keys: peer_multiples (dict per ticker), median_pe, median_ev_ebitda,
            median_ps, implied_value_pe, implied_value_ev_ebitda, implied_value_ps,
            current_price, revenue, ebitda, net_income (for reference).
        """
        if not peers:
            return {
                "peer_multiples": {},
                "median_pe": None,
                "median_ev_ebitda": None,
                "median_ps": None,
                "implied_value_pe": None,
                "implied_value_ev_ebitda": None,
                "implied_value_ps": None,
                "current_price": self._info.get("currentPrice"),
                "message": "Provide a list of peer tickers, e.g. peers=['MSFT','GOOGL']",
            }

        def get_peer_data(t: str) -> Dict[str, Optional[float]]:
            try:
                data = get_yfinance_data(get_ticker_format(t))
                if not data:
                    return {}
                pe = data.get("trailingPE") or data.get("forwardPE")
                ev_ebitda = data.get("enterpriseToEbitda")
                ps = data.get("priceToSalesTrailing12Months")
                return {"pe": pe, "ev_ebitda": ev_ebitda, "ps": ps}
            except Exception:
                return {}

        all_tickers = [self.ticker] + list(peers)
        peer_multiples = {}
        for t in all_tickers:
            peer_multiples[t] = get_peer_data(t)

        pes = [peer_multiples[t]["pe"] for t in peer_multiples if peer_multiples[t].get("pe") is not None]
        ev_ebitdas = [
            peer_multiples[t]["ev_ebitda"]
            for t in peer_multiples
            if peer_multiples[t].get("ev_ebitda") is not None
        ]
        pss = [peer_multiples[t]["ps"] for t in peer_multiples if peer_multiples[t].get("ps") is not None]

        median_pe = float(sorted(pes)[len(pes) // 2]) if pes else None
        median_ev_ebitda = float(sorted(ev_ebitdas)[len(ev_ebitdas) // 2]) if ev_ebitdas else None
        median_ps = float(sorted(pss)[len(pss) // 2]) if pss else None

        # Implied value = multiple * metric (for this stock)
        ttm_eps = self._info.get("trailingEps")
        ebitda = self._info.get("ebitda")
        revenue = self._info.get("totalRevenue")
        shares = self._get_shares()

        implied_value_pe = None
        if median_pe is not None and ttm_eps is not None and ttm_eps > 0:
            implied_value_pe = round(median_pe * ttm_eps, 2)

        implied_value_ev_ebitda = None
        if median_ev_ebitda is not None and ebitda is not None and ebitda > 0 and shares is not None and shares > 0:
            # EV = median_ev_ebitda * ebitda; equity value ≈ EV - net_debt (simplified: use EV/shares as proxy)
            ev_implied = median_ev_ebitda * ebitda
            # Approximate equity value (simplified: ignore net debt for per-share)
            implied_value_ev_ebitda = round(safe_divide(ev_implied, shares) or 0, 2)

        implied_value_ps = None
        if median_ps is not None and revenue is not None and revenue > 0 and shares is not None and shares > 0:
            # Market cap = P/S * revenue => price = (P/S * revenue) / shares
            implied_mcap = median_ps * revenue
            implied_value_ps = round(safe_divide(implied_mcap, shares) or 0, 2)

        return {
            "peer_multiples": peer_multiples,
            "median_pe": median_pe,
            "median_ev_ebitda": median_ev_ebitda,
            "median_ps": median_ps,
            "implied_value_pe": implied_value_pe,
            "implied_value_ev_ebitda": implied_value_ev_ebitda,
            "implied_value_ps": implied_value_ps,
            "current_price": self._info.get("currentPrice"),
            "revenue": revenue,
            "ebitda": ebitda,
            "net_income": self._info.get("netIncomeToCommon"),
        }

    def summary(
        self,
        peers: Optional[List[str]] = None,
        growth_rate: float = 0.05,
        terminal_growth: float = 0.02,
        years: int = 5,
    ) -> Dict[str, Any]:
        """
        Fair value summary combining DCF and comparable companies.

        Args:
            peers: Optional list of peer tickers for comps
            growth_rate: DCF FCF growth rate
            terminal_growth: DCF terminal growth
            years: DCF projection years

        Returns:
            Dict with dcf_result, comps_result, fair_value_low, fair_value_high,
            current_price, and recommendation (undervalued/fair/overvalued).
        """
        dcf_result = self.dcf(growth_rate=growth_rate, terminal_growth=terminal_growth, years=years)
        comps_result = self.comps(peers=peers or [])

        current = self._info.get("currentPrice")
        if current is not None:
            current = float(current)

        values = []
        if dcf_result.get("fair_value_per_share") is not None:
            values.append(dcf_result["fair_value_per_share"])
        for key in ("implied_value_pe", "implied_value_ev_ebitda", "implied_value_ps"):
            v = comps_result.get(key)
            if v is not None and v > 0:
                values.append(v)

        fair_value_low = min(values) if values else None
        fair_value_high = max(values) if values else None

        recommendation = None
        if current is not None and fair_value_low is not None and fair_value_high is not None:
            if current < fair_value_low:
                recommendation = "undervalued"
            elif current > fair_value_high:
                recommendation = "overvalued"
            else:
                recommendation = "fair"

        return {
            "dcf_result": dcf_result,
            "comps_result": comps_result,
            "fair_value_low": fair_value_low,
            "fair_value_high": fair_value_high,
            "current_price": current,
            "recommendation": recommendation,
        }

    def sensitivity(
        self,
        growth_rates: Optional[List[float]] = None,
        wacc_rates: Optional[List[float]] = None,
        years: int = 5,
        terminal_growth: float = 0.02,
    ) -> Dict[str, Any]:
        """
        DCF sensitivity table: fair value per share for different growth and WACC assumptions.

        Args:
            growth_rates: List of FCF growth rates (e.g., [0.03, 0.05, 0.07])
            wacc_rates: List of WACC values (e.g., [0.08, 0.10, 0.12])
            years: DCF projection years
            terminal_growth: Terminal growth rate

        Returns:
            Dict with table (2D dict growth -> wacc -> fair_value), current_price, min_value, max_value.
        """
        growth_rates = growth_rates or [0.03, 0.05, 0.07]
        wacc_rates = wacc_rates or [0.08, 0.10, 0.12]

        table = {}
        all_values = []
        for g in growth_rates:
            table[g] = {}
            for w in wacc_rates:
                dcf = self.dcf(growth_rate=g, wacc=w, years=years, terminal_growth=terminal_growth)
                fv = dcf.get("fair_value_per_share")
                table[g][w] = fv
                if fv is not None:
                    all_values.append(fv)

        current = self._info.get("currentPrice")
        if current is not None:
            current = float(current)

        return {
            "table": table,
            "current_price": current,
            "min_value": min(all_values) if all_values else None,
            "max_value": max(all_values) if all_values else None,
        }
