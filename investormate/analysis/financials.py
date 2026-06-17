"""
Financial statement analysis for InvestorMate.

Common-size, horizontal, vertical, and trend analysis on yfinance statements.
"""

import csv
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from ..utils.exceptions import ValidationError
from ..utils.helpers import safe_divide


def _sorted_periods(statement: Dict) -> List[str]:
    return sorted(statement.keys(), reverse=True)


def _get_line_item(statement: Dict, period: str, *names: str) -> Optional[float]:
    if period not in statement:
        return None
    row = statement[period]
    for name in names:
        if name in row and row[name] is not None:
            return float(row[name])
    return None


class FinancialStatements:
    """
    Financial statement analysis toolkit.

    Example:
        >>> stock = Stock("AAPL")
        >>> stock.financials.common_size("income")
        >>> stock.financials.horizontal(periods=3)
    """

    def __init__(
        self,
        ticker: str,
        info: Optional[Dict] = None,
        balance_sheet: Optional[Dict] = None,
        income_stmt: Optional[Dict] = None,
        cash_flow: Optional[Dict] = None,
    ):
        self.ticker = ticker
        self.info = info or {}
        self.balance_sheet = balance_sheet or {}
        self.income_stmt = income_stmt or {}
        self.cash_flow = cash_flow or {}

    def _statement_for(self, kind: str) -> Dict:
        if kind in ("income", "income_statement"):
            return self.income_stmt
        if kind in ("balance_sheet", "balance"):
            return self.balance_sheet
        if kind in ("cash_flow", "cashflow"):
            return self.cash_flow
        raise ValidationError(
            f"Unknown statement type: {kind}. Use income, balance_sheet, or cash_flow."
        )

    def common_size(
        self, statement_type: str = "income"
    ) -> Dict[str, Dict[str, Optional[float]]]:
        """
        Common-size analysis: each line item as % of revenue (income) or total assets (balance).
        """
        stmt = self._statement_for(statement_type)
        if not stmt:
            return {}

        result: Dict[str, Dict[str, Optional[float]]] = {}
        for period in _sorted_periods(stmt):
            rows = stmt[period]
            if statement_type.startswith("income"):
                base = _get_line_item(
                    stmt, period, "Total Revenue", "TotalRevenue", "Revenue"
                )
            else:
                base = _get_line_item(stmt, period, "Total Assets", "TotalAssets")
            if not base:
                continue
            result[period] = {
                item: safe_divide(val, base)
                for item, val in rows.items()
                if val is not None
            }
        return result

    def horizontal(self, periods: int = 5) -> Dict[str, Any]:
        """
        Year-over-year dollar and percent changes across line items.
        """
        stmt = self.income_stmt or self.balance_sheet
        if not stmt:
            return {"periods": [], "changes": {}}

        period_list = _sorted_periods(stmt)[: periods + 1]
        if len(period_list) < 2:
            return {"periods": period_list, "changes": {}}

        changes: Dict[str, List[Dict[str, Any]]] = {}
        for i in range(len(period_list) - 1):
            newer, older = period_list[i], period_list[i + 1]
            newer_rows = stmt.get(newer, {})
            older_rows = stmt.get(older, {})
            all_items = set(newer_rows.keys()) | set(older_rows.keys())
            for item in all_items:
                v_new = newer_rows.get(item)
                v_old = older_rows.get(item)
                if v_new is None or v_old is None:
                    continue
                dollar_chg = v_new - v_old
                pct_chg = safe_divide(dollar_chg, abs(v_old)) if v_old != 0 else None
                changes.setdefault(item, []).append(
                    {
                        "from_period": older,
                        "to_period": newer,
                        "dollar_change": dollar_chg,
                        "percent_change": pct_chg,
                    }
                )

        return {"periods": period_list, "changes": changes}

    def vertical(self, period: Optional[str] = None) -> Dict[str, Optional[float]]:
        """
        Component breakdown within a single period (common-size for one period).
        """
        stmt = self.income_stmt
        if not stmt:
            return {}
        period_key = period or _sorted_periods(stmt)[0]
        cs = self.common_size("income")
        return cs.get(period_key, {})

    def trend(self, base_year: Optional[Union[str, int]] = None) -> Dict[str, Any]:
        """
        Multi-year indexed trends (base year = 100).
        """
        stmt = self.income_stmt
        if not stmt:
            return {"base_period": None, "indexed": {}}

        periods = _sorted_periods(stmt)
        if base_year is not None:
            base_str = str(base_year)
            base_period = next(
                (p for p in periods if p.startswith(base_str)), periods[-1]
            )
        else:
            base_period = periods[-1] if periods else None

        if not base_period:
            return {"base_period": None, "indexed": {}}

        base_rows = stmt[base_period]
        indexed: Dict[str, Dict[str, Optional[float]]] = {}
        for period in periods:
            rows = stmt[period]
            indexed[period] = {}
            for item, base_val in base_rows.items():
                if base_val is None or base_val == 0:
                    continue
                cur = rows.get(item)
                if cur is not None:
                    indexed[period][item] = round(100 * cur / base_val, 2)

        return {"base_period": base_period, "indexed": indexed}

    def cash_flow_quality(self) -> Dict[str, Any]:
        """
        Operating cash flow vs net income and accruals ratio.
        """
        if not self.cash_flow or not self.income_stmt:
            return {
                "operating_cash_flow": None,
                "net_income": None,
                "ocf_to_ni": None,
                "accruals_ratio": None,
                "assessment": "Insufficient statement data",
            }

        period = _sorted_periods(self.cash_flow)[0]
        ocf = _get_line_item(
            self.cash_flow,
            period,
            "Operating Cash Flow",
            "Total Cash From Operating Activities",
            "OperatingCashFlow",
        )
        ni = _get_line_item(
            self.income_stmt,
            period,
            "Net Income",
            "NetIncome",
            "Net Income Common Stockholders",
        )
        total_assets = self.info.get("totalAssets")
        ocf_to_ni = safe_divide(ocf, ni)
        accruals = None
        if ocf is not None and ni is not None and total_assets:
            accruals = safe_divide(ni - ocf, total_assets)

        assessment = "Healthy cash conversion"
        if ocf_to_ni is not None and ocf_to_ni < 0.8:
            assessment = "Net income exceeds operating cash flow — review accruals"
        elif ocf_to_ni is not None and ocf_to_ni > 1.2:
            assessment = "Strong cash generation relative to earnings"

        return {
            "period": period,
            "operating_cash_flow": ocf,
            "net_income": ni,
            "ocf_to_ni": ocf_to_ni,
            "accruals_ratio": accruals,
            "assessment": assessment,
        }

    def to_csv(self, path: str, statement_type: str = "income") -> str:
        """Export raw statement to CSV."""
        stmt = self._statement_for(statement_type)
        if not stmt:
            raise ValidationError(f"No {statement_type} data to export")

        periods = _sorted_periods(stmt)
        items = sorted({k for p in periods for k in stmt[p].keys()})
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["line_item"] + periods)
            for item in items:
                writer.writerow([item] + [stmt[p].get(item) for p in periods])
        return path

    def to_dataframe(self, statement_type: str = "income") -> pd.DataFrame:
        """Return statement as a DataFrame (periods as columns)."""
        stmt = self._statement_for(statement_type)
        if not stmt:
            return pd.DataFrame()
        return pd.DataFrame.from_dict(stmt, orient="index").T
