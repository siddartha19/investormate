"""
Financial scoring systems for InvestorMate.
Piotroski F-Score, Altman Z-Score, Beneish M-Score.
"""

from typing import Any, Dict, List, Optional, Tuple

from ..utils.helpers import safe_divide


def _sorted_period_keys(stmt: Dict) -> List[str]:
    """Return statement period keys sorted newest-first."""
    if not stmt:
        return []
    return sorted(stmt.keys(), reverse=True)


def _get_line(
    period_data: Optional[Dict[str, Any]], possible_names: Tuple[str, ...]
) -> Optional[float]:
    """Get first matching line item value from a period's row dict."""
    if not period_data:
        return None
    for name in possible_names:
        if name in period_data and period_data[name] is not None:
            try:
                return float(period_data[name])
            except (TypeError, ValueError):
                continue
    return None


def _beneish_compute_indices(
    balance_sheet: Dict,
    income_stmt: Dict,
    cash_flow: Dict,
) -> Tuple[Optional[Dict[str, float]], str]:
    """
    Compute Beneish M-Score 8 indices from two fiscal periods (t, t-1).

    Returns:
        (indices dict or None, error/reason message if incomplete)
    """
    bs_keys = _sorted_period_keys(balance_sheet)
    is_keys = _sorted_period_keys(income_stmt)
    cf_keys = _sorted_period_keys(cash_flow)

    if len(bs_keys) < 2 or len(is_keys) < 2:
        return None, "Need at least two periods of balance sheet and income statement"

    # Align periods: use intersection of dates, newest two
    common = sorted(set(bs_keys) & set(is_keys), reverse=True)
    if len(common) < 2:
        return None, "Insufficient overlapping statement periods"

    t_key, tm1_key = common[0], common[1]

    def bs(period: str) -> Optional[Dict]:
        return balance_sheet.get(period)

    def inc(period: str) -> Optional[Dict]:
        return income_stmt.get(period)

    def cf_for_period(period: str) -> Optional[Dict]:
        """Match cash flow to nearest available period."""
        if period in cash_flow:
            return cash_flow[period]
        # try same year from cf_keys
        for k in cf_keys:
            if k[:4] == period[:4]:
                return cash_flow[k]
        return None

    # Line item aliases (yfinance naming varies)
    AR = (
        "Accounts Receivable",
        "Net Receivables",
        "Trade And Other Receivables Net",
    )
    REV = ("Total Revenue", "Total Revenues", "Revenue")
    COGS = ("Cost Of Revenue", "Cost of Revenue", "Cost Of Goods Sold")
    CA = ("Total Current Assets",)
    PPE = (
        "Net PPE",
        "Property Plant And Equipment Net",
        "Property Plant Equipment Net",
    )
    TA = ("Total Assets",)
    TL = (
        "Total Liabilities Net Minority Interest",
        "Total Liab",
        "Total Liabilities",
    )
    DEP = (
        "Reconciled Depreciation",
        "Depreciation And Amortization",
        "Depreciation Amortization Depletion",
    )
    SGA = (
        "Selling General And Administration",
        "Selling General And Administrative Expense",
        "Selling, General & Administration",
    )
    NI = (
        "Net Income",
        "Net Income Common Stockholders",
        "Net Income From Continuing Operations",
    )
    OCF = (
        "Operating Cash Flow",
        "Total Cash From Operating Activities",
        "Cash Flow From Continuing Operating Activities",
    )

    sales_t = _get_line(inc(t_key), REV)
    sales_tm1 = _get_line(inc(tm1_key), REV)
    ar_t = _get_line(bs(t_key), AR)
    ar_tm1 = _get_line(bs(tm1_key), AR)
    cogs_t = _get_line(inc(t_key), COGS)
    cogs_tm1 = _get_line(inc(tm1_key), COGS)
    ca_t = _get_line(bs(t_key), CA)
    ca_tm1 = _get_line(bs(tm1_key), CA)
    ppe_t = _get_line(bs(t_key), PPE)
    ppe_tm1 = _get_line(bs(tm1_key), PPE)
    ta_t = _get_line(bs(t_key), TA)
    ta_tm1 = _get_line(bs(tm1_key), TA)
    tl_t = _get_line(bs(t_key), TL)
    tl_tm1 = _get_line(bs(tm1_key), TL)
    dep_t = _get_line(inc(t_key), DEP) or _get_line(cf_for_period(t_key), DEP)
    dep_tm1 = _get_line(inc(tm1_key), DEP) or _get_line(cf_for_period(tm1_key), DEP)
    sga_t = _get_line(inc(t_key), SGA)
    sga_tm1 = _get_line(inc(tm1_key), SGA)
    ni_t = _get_line(inc(t_key), NI)
    ocf_t = _get_line(cf_for_period(t_key), OCF)

    if sales_t is None or sales_tm1 is None or sales_tm1 == 0:
        return None, "Missing revenue for two periods"
    if ta_t is None or ta_tm1 is None or ta_t == 0 or ta_tm1 == 0:
        return None, "Missing total assets for two periods"

    # Gross margin components
    gm_t = None
    gm_tm1 = None
    if sales_t and cogs_t is not None:
        gm_t = (sales_t - cogs_t) / sales_t
    if sales_tm1 and cogs_tm1 is not None:
        gm_tm1 = (sales_tm1 - cogs_tm1) / sales_tm1

    indices: Dict[str, float] = {}

    # DSRI
    if ar_t is not None and ar_tm1 is not None and sales_t and sales_tm1:
        r_t = ar_t / sales_t
        r_tm1 = ar_tm1 / sales_tm1
        indices["DSRI"] = safe_divide(r_t, r_tm1, default=1.0) or 1.0
    else:
        indices["DSRI"] = 1.0

    # GMI
    if gm_t and gm_tm1 and gm_t > 0:
        indices["GMI"] = safe_divide(gm_tm1, gm_t, default=1.0) or 1.0
    else:
        indices["GMI"] = 1.0

    # AQI: [1 - (CA+PPE)/TA] ratio year over year
    if all(x is not None for x in (ca_t, ppe_t, ta_t, ca_tm1, ppe_tm1, ta_tm1)):
        aqi_t = 1.0 - (ca_t + ppe_t) / ta_t
        aqi_tm1 = 1.0 - (ca_tm1 + ppe_tm1) / ta_tm1
        indices["AQI"] = safe_divide(aqi_t, aqi_tm1, default=1.0) or 1.0
    else:
        indices["AQI"] = 1.0

    # SGI
    indices["SGI"] = safe_divide(sales_t, sales_tm1, default=1.0) or 1.0

    # DEPI: depreciation rate t-1 / depreciation rate t
    # rate = Depreciation / (PPE + Depreciation)
    def dep_rate(dep: Optional[float], ppe: Optional[float]) -> Optional[float]:
        if dep is None or ppe is None:
            return None
        denom = ppe + dep
        if denom == 0:
            return None
        return dep / denom

    dr_t = dep_rate(dep_t, ppe_t)
    dr_tm1 = dep_rate(dep_tm1, ppe_tm1)
    if dr_t and dr_tm1 and dr_t > 0:
        indices["DEPI"] = safe_divide(dr_tm1, dr_t, default=1.0) or 1.0
    else:
        indices["DEPI"] = 1.0

    # SGAI
    if sga_t is not None and sga_tm1 is not None and sales_t and sales_tm1:
        indices["SGAI"] = (
            safe_divide((sga_t / sales_t), (sga_tm1 / sales_tm1), default=1.0) or 1.0
        )
    else:
        indices["SGAI"] = 1.0

    # TATA = (Net Income - Operating Cash Flow) / Total Assets
    if ni_t is not None and ocf_t is not None and ta_t:
        indices["TATA"] = (ni_t - ocf_t) / ta_t
    else:
        indices["TATA"] = 0.0

    # LVGI
    if tl_t is not None and tl_tm1 is not None and ta_t and ta_tm1:
        lev_t = tl_t / ta_t
        lev_tm1 = tl_tm1 / ta_tm1
        indices["LVGI"] = safe_divide(lev_t, lev_tm1, default=1.0) or 1.0
    else:
        indices["LVGI"] = 1.0

    return indices, ""


def _beneish_m_from_indices(indices: Dict[str, float]) -> float:
    """Beneish (1999) M-Score formula."""
    return (
        -4.84
        + 0.920 * indices["DSRI"]
        + 0.528 * indices["GMI"]
        + 0.404 * indices["AQI"]
        + 0.892 * indices["SGI"]
        + 0.115 * indices["DEPI"]
        - 0.172 * indices["SGAI"]
        + 4.679 * indices["TATA"]
        - 0.327 * indices["LVGI"]
    )


class FinancialScores:
    """Calculator for financial health scores."""

    def __init__(
        self,
        stock_info: Dict,
        balance_sheet: Optional[Dict] = None,
        income_stmt: Optional[Dict] = None,
        cash_flow: Optional[Dict] = None,
    ):
        """
        Initialize financial scores calculator.

        Args:
            stock_info: Stock info dictionary from yfinance
            balance_sheet: Balance sheet data (optional)
            income_stmt: Income statement data (optional)
            cash_flow: Cash flow data (optional)
        """
        self.info = stock_info
        self.balance_sheet = balance_sheet or {}
        self.income_stmt = income_stmt or {}
        self.cash_flow = cash_flow or {}

    def piotroski_score(self) -> Tuple[int, Dict[str, int]]:
        """
        Calculate Piotroski F-Score (0-9).

        A score of 8-9 indicates a very strong company.
        A score of 0-2 indicates a weak company.

        Returns:
            Tuple of (total_score, breakdown_dict)
        """
        breakdown = {}

        # Profitability (4 points)
        # 1. Positive net income
        net_income = self.info.get("netIncomeToCommon", 0)
        breakdown["net_income"] = 1 if net_income > 0 else 0

        # 2. Positive ROA
        roa = self.info.get("returnOnAssets", 0)
        breakdown["roa"] = 1 if roa and roa > 0 else 0

        # 3. Positive operating cash flow
        operating_cf = self.info.get("operatingCashflow", 0)
        breakdown["operating_cf"] = 1 if operating_cf and operating_cf > 0 else 0

        # 4. Cash flow from operations > net income (quality of earnings)
        breakdown["cf_quality"] = (
            1 if operating_cf and net_income and operating_cf > net_income else 0
        )

        # Leverage, Liquidity & Source of Funds (3 points)
        # 5. Lower long-term debt ratio this year
        # (simplified: check if debt-to-equity is reasonable)
        debt_to_equity = self.info.get("debtToEquity", 100)
        breakdown["debt"] = 1 if debt_to_equity and debt_to_equity < 80 else 0

        # 6. Higher current ratio this year
        current_ratio = self.info.get("currentRatio", 0)
        breakdown["current_ratio"] = 1 if current_ratio and current_ratio > 1.0 else 0

        # 7. No new shares issued
        # (simplified: assume yes if shares outstanding is stable)
        breakdown["no_dilution"] = (
            1  # Default to 1, hard to calculate from single point
        )

        # Operating Efficiency (2 points)
        # 8. Higher gross margin this year
        gross_margin = self.info.get("grossMargins", 0)
        breakdown["gross_margin"] = 1 if gross_margin and gross_margin > 0.20 else 0

        # 9. Higher asset turnover this year
        revenue = self.info.get("totalRevenue", 0)
        total_assets = self.info.get("totalAssets", 1)
        asset_turnover = safe_divide(revenue, total_assets, 0)
        breakdown["asset_turnover"] = (
            1 if asset_turnover and asset_turnover > 0.5 else 0
        )

        total_score = sum(breakdown.values())
        return total_score, breakdown

    def altman_z_score(self) -> Tuple[Optional[float], str]:
        """
        Calculate Altman Z-Score (bankruptcy prediction).

        Z > 2.99: Safe zone (low bankruptcy risk)
        1.81 < Z < 2.99: Grey zone
        Z < 1.81: Distress zone (high bankruptcy risk)

        Returns:
            Tuple of (z_score, interpretation)
        """
        # Get financial data
        total_assets = self.info.get("totalAssets")
        total_liabilities = self.info.get("totalLiabilities")
        total_equity = self.info.get("totalStockholderEquity")
        current_assets = self.info.get("totalCurrentAssets")
        current_liabilities = self.info.get("totalCurrentLiabilities")
        retained_earnings = self.info.get("retainedEarnings")
        ebit = self.info.get("ebit")
        revenue = self.info.get("totalRevenue")
        market_cap = self.info.get("marketCap")

        # Check if we have enough data
        if not all(
            [total_assets, total_liabilities, current_assets, current_liabilities]
        ):
            return None, "Insufficient data for Z-Score calculation"

        # Calculate working capital
        working_capital = (current_assets or 0) - (current_liabilities or 0)

        # Calculate components
        # X1 = Working Capital / Total Assets
        x1 = safe_divide(working_capital, total_assets, 0) * 1.2

        # X2 = Retained Earnings / Total Assets
        x2 = safe_divide(retained_earnings or 0, total_assets, 0) * 1.4

        # X3 = EBIT / Total Assets
        x3 = safe_divide(ebit or 0, total_assets, 0) * 3.3

        # X4 = Market Cap / Total Liabilities
        x4 = safe_divide(market_cap or 0, total_liabilities, 0) * 0.6

        # X5 = Revenue / Total Assets
        x5 = safe_divide(revenue or 0, total_assets, 0) * 1.0

        # Calculate Z-Score
        z_score = x1 + x2 + x3 + x4 + x5

        # Interpret
        if z_score > 2.99:
            interpretation = "Safe Zone - Low bankruptcy risk"
        elif z_score > 1.81:
            interpretation = "Grey Zone - Moderate risk"
        else:
            interpretation = "Distress Zone - High bankruptcy risk"

        return z_score, interpretation

    def beneish_m_score_detail(self) -> Dict[str, Any]:
        """
        Full Beneish M-Score (Beneish 1999) with eight indices.

        Requires two fiscal periods in balance sheet, income statement, and
        preferably cash flow (for TATA). Missing line items default individual
        indices to neutral values (1.0) where documented in Beneish literature;
        TATA defaults to 0.0 if accruals cannot be computed.

        Returns:
            Dict with keys: score, interpretation, indices, method, note, periods_used
        """
        indices, err = _beneish_compute_indices(
            self.balance_sheet, self.income_stmt, self.cash_flow
        )
        if indices is None:
            return {
                "score": None,
                "interpretation": err or "Insufficient data",
                "indices": None,
                "method": "full_8_variable",
                "note": err,
                "periods_used": None,
            }

        m_score = _beneish_m_from_indices(indices)
        if m_score < -2.22:
            interpretation = "Low risk of earnings manipulation (M < -2.22)"
        else:
            interpretation = (
                "Possible earnings manipulation — investigate further (M > -2.22)"
            )

        common = sorted(
            set(self.balance_sheet.keys()) & set(self.income_stmt.keys()), reverse=True
        )
        periods_used = common[:2] if len(common) >= 2 else common

        return {
            "score": m_score,
            "interpretation": interpretation,
            "indices": indices.copy(),
            "method": "full_8_variable",
            "note": (
                "Uses yfinance statement line items; some indices may be neutral (1.0) "
                "if fields are missing. Compare to sector peers before concluding."
            ),
            "periods_used": periods_used,
        }

    def beneish_m_score(self) -> Tuple[Optional[float], str]:
        """
        Calculate Beneish M-Score (earnings manipulation detection).

        Uses the full eight-variable model when two periods of statements exist;
        otherwise falls back to a simplified proxy score from trailing metrics.

        M-Score < -2.22: Unlikely to be manipulating earnings
        M-Score > -2.22: Possible earnings manipulation

        Returns:
            Tuple of (m_score, interpretation)
        """
        detail = self.beneish_m_score_detail()
        if detail["score"] is not None:
            return detail["score"], detail["interpretation"]

        # Fallback proxy when statements insufficient
        debt_to_equity = self.info.get("debtToEquity", 0)
        gross_margin = self.info.get("grossMargins", 0)
        asset_turnover = safe_divide(
            self.info.get("totalRevenue", 0),
            self.info.get("totalAssets", 1),
            0,
        )

        risk_score = 0
        if debt_to_equity and debt_to_equity > 100:
            risk_score += 1
        if gross_margin and gross_margin < 0.15:
            risk_score += 1
        if asset_turnover < 0.5:
            risk_score += 1

        m_score = -3.0 + (risk_score * 0.5)
        if m_score < -2.22:
            interpretation = (
                "Low risk (proxy — add multi-period statements for full Beneish)"
            )
        else:
            interpretation = (
                "Elevated proxy risk — use full statements for Beneish M-Score"
            )

        return m_score, interpretation

    def all_scores(self) -> Dict:
        """
        Get all financial scores.

        Returns:
            Dictionary with all scores
        """
        piotroski, piotroski_breakdown = self.piotroski_score()
        altman, altman_interp = self.altman_z_score()
        beneish, beneish_interp = self.beneish_m_score()
        beneish_detail = self.beneish_m_score_detail()

        return {
            "piotroski": {
                "score": piotroski,
                "max": 9,
                "breakdown": piotroski_breakdown,
                "interpretation": self._interpret_piotroski(piotroski),
            },
            "altman_z": {"score": altman, "interpretation": altman_interp},
            "beneish_m": {
                "score": beneish,
                "interpretation": beneish_interp,
                "indices": beneish_detail.get("indices"),
                "method": beneish_detail.get("method"),
                "periods_used": beneish_detail.get("periods_used"),
                "note": beneish_detail.get("note"),
            },
        }

    @staticmethod
    def _interpret_piotroski(score: int) -> str:
        """Interpret Piotroski F-Score."""
        if score >= 8:
            return "Very Strong - Excellent financial health"
        elif score >= 6:
            return "Strong - Good financial health"
        elif score >= 4:
            return "Moderate - Average financial health"
        elif score >= 2:
            return "Weak - Below average financial health"
        else:
            return "Very Weak - Poor financial health"
