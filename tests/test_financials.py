"""Tests for financial statement analysis."""

import pytest

from investormate.analysis.financials import FinancialStatements


INCOME = {
    "2024-12-31": {
        "Total Revenue": 1000.0,
        "Cost Of Revenue": 600.0,
        "Net Income": 100.0,
    },
    "2023-12-31": {
        "Total Revenue": 900.0,
        "Cost Of Revenue": 550.0,
        "Net Income": 80.0,
    },
}

BALANCE = {
    "2024-12-31": {
        "Total Assets": 2000.0,
        "Total Current Assets": 800.0,
        "Total Current Liabilities": 400.0,
    }
}

CASH_FLOW = {
    "2024-12-31": {
        "Operating Cash Flow": 120.0,
    }
}


class TestFinancialStatements:
    def test_common_size_income(self):
        fs = FinancialStatements("TEST", income_stmt=INCOME)
        cs = fs.common_size("income")
        assert "2024-12-31" in cs
        assert cs["2024-12-31"]["Total Revenue"] == pytest.approx(1.0)
        assert cs["2024-12-31"]["Net Income"] == pytest.approx(0.1)

    def test_horizontal(self):
        fs = FinancialStatements("TEST", income_stmt=INCOME)
        result = fs.horizontal(periods=2)
        assert len(result["periods"]) >= 2
        assert "Total Revenue" in result["changes"]

    def test_trend(self):
        fs = FinancialStatements("TEST", income_stmt=INCOME)
        trend = fs.trend(base_year=2023)
        assert trend["base_period"] is not None
        assert "2024-12-31" in trend["indexed"]

    def test_cash_flow_quality(self):
        fs = FinancialStatements(
            "TEST",
            info={"totalAssets": 2000},
            income_stmt=INCOME,
            cash_flow=CASH_FLOW,
        )
        q = fs.cash_flow_quality()
        assert q["ocf_to_ni"] == pytest.approx(1.2)
        assert "assessment" in q

    def test_to_csv(self, tmp_path):
        fs = FinancialStatements("TEST", income_stmt=INCOME)
        path = tmp_path / "income.csv"
        fs.to_csv(str(path), "income")
        assert path.exists()
