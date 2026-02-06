"""Tests for valuation module (DCF, comps, summary)."""

import pytest
from unittest.mock import patch
from investormate import Stock
from investormate.analysis.valuation import Valuation


def _make_ratios_mock(wacc=0.10):
    m = pytest.importorskip("unittest.mock").MagicMock()
    m.wacc = wacc
    return m


class TestValuationDCF:
    """Test DCF valuation."""

    def test_dcf_returns_dict_with_expected_keys(self):
        """DCF result has expected structure."""
        info = {
            "freeCashflow": 100_000_000,
            "sharesOutstanding": 1_000_000,
        }
        v = Valuation("TEST", info=info, ratios=_make_ratios_mock(0.10))
        result = v.dcf(growth_rate=0.05, years=5)
        assert "fair_value_per_share" in result
        assert "enterprise_value" in result
        assert "dcf_value" in result
        assert "terminal_value_pv" in result
        assert "fcf_series" in result
        assert "wacc_used" in result
        assert "assumptions" in result
        assert result["fair_value_per_share"] is not None
        assert len(result["fcf_series"]) == 5

    def test_dcf_missing_fcf_returns_none_fair_value(self):
        """When FCF is missing, fair_value_per_share is None."""
        info = {"sharesOutstanding": 1_000_000}
        v = Valuation("TEST", info=info)
        result = v.dcf(growth_rate=0.05)
        assert result["fair_value_per_share"] is None
        assert result["fcf_series"] == []

    def test_dcf_uses_provided_wacc(self):
        """DCF uses explicitly provided WACC."""
        info = {"freeCashflow": 1e9, "sharesOutstanding": 1e8}
        v = Valuation("TEST", info=info)
        result = v.dcf(growth_rate=0.05, wacc=0.12)
        assert result["wacc_used"] == 0.12

    def test_dcf_with_terminal_multiple(self):
        """DCF with terminal_multiple uses exit multiple instead of perpetuity growth."""
        info = {"freeCashflow": 100_000_000, "sharesOutstanding": 1_000_000}
        v = Valuation("TEST", info=info, ratios=_make_ratios_mock(0.10))
        result_perp = v.dcf(growth_rate=0.05, years=5, terminal_growth=0.02)
        result_mult = v.dcf(growth_rate=0.05, years=5, terminal_multiple=15)
        assert result_mult["fair_value_per_share"] is not None
        assert result_mult["assumptions"]["terminal_multiple"] == 15
        # With terminal multiple, result can differ from perpetuity
        assert result_mult["fair_value_per_share"] != result_perp["fair_value_per_share"]


class TestValuationComps:
    """Test comparable companies valuation."""

    def test_comps_without_peers_returns_message(self):
        """Comps without peers returns message and empty peer_multiples."""
        v = Valuation("TEST", info={})
        result = v.comps(peers=None)
        assert "peer_multiples" in result
        assert result["peer_multiples"] == {}
        assert "message" in result

    @patch("investormate.analysis.valuation.get_yfinance_data")
    def test_comps_with_peers_returns_structure(self, mock_get):
        """Comps with peers returns median and implied values structure."""
        mock_get.return_value = {
            "trailingPE": 25.0,
            "enterpriseToEbitda": 15.0,
            "priceToSalesTrailing12Months": 5.0,
            "currentPrice": 150.0,
        }
        info = {
            "trailingEps": 6.0,
            "ebitda": 10e9,
            "totalRevenue": 50e9,
            "sharesOutstanding": 1e9,
            "currentPrice": 150.0,
        }
        v = Valuation("TEST", info=info)
        result = v.comps(peers=["PEER1", "PEER2"])
        assert "median_pe" in result
        assert "implied_value_pe" in result
        assert "peer_multiples" in result
        assert "TEST" in result["peer_multiples"] or "PEER1" in result["peer_multiples"]


class TestValuationSummary:
    """Test fair value summary."""

    def test_summary_returns_recommendation_and_range(self):
        """Summary returns recommendation and fair value range."""
        info = {
            "freeCashflow": 100_000_000,
            "sharesOutstanding": 1_000_000,
            "currentPrice": 50.0,
        }
        v = Valuation("TEST", info=info, ratios=_make_ratios_mock(0.10))
        result = v.summary(peers=None)
        assert "recommendation" in result
        assert "fair_value_low" in result
        assert "fair_value_high" in result
        assert "current_price" in result
        assert "dcf_result" in result
        assert "comps_result" in result

    def test_summary_returns_implied_upside_downside(self):
        """Summary returns implied_upside_pct and implied_downside_pct vs current price."""
        info = {
            "freeCashflow": 100_000_000,
            "sharesOutstanding": 1_000_000,
            "currentPrice": 50.0,
        }
        v = Valuation("TEST", info=info, ratios=_make_ratios_mock(0.10))
        result = v.summary(peers=None)
        assert "implied_upside_pct" in result
        assert "implied_downside_pct" in result
        assert "fair_value_mid" in result
        if result["fair_value_high"] and result["current_price"]:
            assert result["implied_upside_pct"] is not None
        if result["fair_value_low"] and result["current_price"]:
            assert result["implied_downside_pct"] is not None


class TestValuationSensitivity:
    """Test DCF sensitivity table."""

    def test_sensitivity_returns_table_structure(self):
        """Sensitivity returns 2D table and min/max."""
        info = {
            "freeCashflow": 1e9,
            "sharesOutstanding": 1e8,
        }
        v = Valuation("TEST", info=info)
        result = v.sensitivity(
            growth_rates=[0.03, 0.05],
            wacc_rates=[0.08, 0.10],
        )
        assert "table" in result
        assert 0.03 in result["table"]
        assert 0.08 in result["table"][0.03]
        assert "min_value" in result
        assert "max_value" in result


class TestStockValuationIntegration:
    """Test Stock.valuation property."""

    def test_stock_has_valuation_property(self):
        """Stock has valuation property returning Valuation instance."""
        stock = Stock("AAPL")
        v = stock.valuation
        assert isinstance(v, Valuation)
        assert v.ticker == "AAPL"

    def test_stock_valuation_dcf_callable(self):
        """Stock.valuation.dcf() is callable and returns dict."""
        stock = Stock("AAPL")
        result = stock.valuation.dcf(growth_rate=0.05)
        assert isinstance(result, dict)
        assert "fair_value_per_share" in result
        assert "assumptions" in result
