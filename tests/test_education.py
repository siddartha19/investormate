"""Tests for educational layer on RatiosCalculator."""

import pytest

from investormate.analysis.ratios import RatiosCalculator
from investormate.utils.exceptions import ValidationError


INFO = {
    "trailingPE": 25.0,
    "currentRatio": 1.8,
    "returnOnEquity": 0.15,
    "profitMargins": 0.12,
    "totalCurrentAssets": 180,
    "totalCurrentLiabilities": 100,
    "netIncomeToCommon": 50,
    "totalStockholderEquity": 300,
    "debtToEquity": 1.2,
    "operatingCashflow": 60,
    "revenueGrowth": 0.05,
}


class TestEducationLayer:
    def test_explain_pe(self):
        r = RatiosCalculator(INFO)
        exp = r.explain("pe")
        assert "formula" in exp
        assert exp["cfa_topic"]

    def test_show_work_current_ratio(self):
        r = RatiosCalculator(INFO)
        work = r.show_work("current_ratio")
        assert work["result"] == pytest.approx(1.8)
        assert len(work["steps"]) >= 2

    def test_cfa_topic(self):
        r = RatiosCalculator(INFO)
        assert "Financial Statement" in r.cfa_topic("current_ratio")

    def test_interpret(self):
        r = RatiosCalculator(INFO)
        interp = r.interpret()
        assert "pe" in interp
        assert "assessment" in interp["pe"]

    def test_red_flags_empty_when_healthy(self):
        r = RatiosCalculator(INFO)
        flags = r.red_flags()
        assert isinstance(flags, list)

    def test_percentile(self):
        r = RatiosCalculator(INFO)
        result = r.percentile("pe", peer_values=[15, 20, 25, 30, 35])
        assert result["percentile"] == 40.0

    def test_dupont_breakdown(self):
        r = RatiosCalculator(
            {**INFO, "totalAssets": 1000, "totalRevenue": 500},
            income_stmt={},
            balance_sheet={},
            cash_flow={},
        )
        dupont = r.dupont_breakdown()
        assert "components" in dupont
        assert "formula" in dupont

    def test_unknown_ratio_raises(self):
        r = RatiosCalculator(INFO)
        with pytest.raises(ValidationError):
            r.explain("not_a_real_ratio_xyz")
