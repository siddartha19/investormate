"""
Tests for advanced financial ratios and TTM metrics.
"""

import pytest
from investormate import Stock


class TestTTMMetrics:
    """Test TTM (Trailing Twelve Months) metrics."""
    
    @pytest.fixture
    def stock(self):
        """Create a stock instance for testing."""
        return Stock("AAPL")
    
    def test_ttm_eps(self, stock):
        """Test TTM EPS calculation."""
        ttm_eps = stock.ratios.ttm_eps
        assert ttm_eps is None or isinstance(ttm_eps, (int, float))
    
    def test_ttm_pe(self, stock):
        """Test TTM P/E ratio."""
        ttm_pe = stock.ratios.ttm_pe
        assert ttm_pe is None or isinstance(ttm_pe, (int, float))
        if ttm_pe is not None:
            assert ttm_pe > 0  # P/E should be positive for profitable companies
    
    def test_ttm_revenue(self, stock):
        """Test TTM revenue calculation."""
        ttm_revenue = stock.ratios.ttm_revenue
        assert ttm_revenue is None or isinstance(ttm_revenue, (int, float))
        if ttm_revenue is not None:
            assert ttm_revenue > 0
    
    def test_ttm_net_income(self, stock):
        """Test TTM net income calculation."""
        ttm_net_income = stock.ratios.ttm_net_income
        assert ttm_net_income is None or isinstance(ttm_net_income, (int, float))
    
    def test_ttm_ebitda(self, stock):
        """Test TTM EBITDA."""
        ttm_ebitda = stock.ratios.ttm_ebitda
        assert ttm_ebitda is None or isinstance(ttm_ebitda, (int, float))
    
    def test_ttm_metrics_method(self, stock):
        """Test the ttm_metrics() method returns all TTM metrics."""
        ttm_metrics = stock.ratios.ttm_metrics()
        
        assert isinstance(ttm_metrics, dict)
        assert 'ttm_eps' in ttm_metrics
        assert 'ttm_pe' in ttm_metrics
        assert 'ttm_revenue' in ttm_metrics
        assert 'ttm_net_income' in ttm_metrics
        assert 'ttm_ebitda' in ttm_metrics


class TestAdvancedRatios:
    """Test advanced profitability and capital structure ratios."""
    
    @pytest.fixture
    def stock(self):
        """Create a stock instance for testing."""
        return Stock("AAPL")
    
    def test_roic(self, stock):
        """Test ROIC calculation."""
        roic = stock.ratios.roic
        assert roic is None or isinstance(roic, (int, float))
        if roic is not None:
            # ROIC should typically be between -100% and 100%
            assert -1 <= roic <= 1
    
    def test_wacc(self, stock):
        """Test WACC calculation."""
        wacc = stock.ratios.wacc
        assert wacc is None or isinstance(wacc, (int, float))
        if wacc is not None:
            # WACC should typically be between 0% and 50%
            assert 0 <= wacc <= 0.5
    
    def test_equity_multiplier(self, stock):
        """Test equity multiplier calculation."""
        equity_multiplier = stock.ratios.equity_multiplier
        assert equity_multiplier is None or isinstance(equity_multiplier, (int, float))
        if equity_multiplier is not None:
            # Equity multiplier should be >= 1
            assert equity_multiplier >= 1
    
    def test_dupont_roe(self, stock):
        """Test DuPont ROE analysis."""
        dupont = stock.ratios.dupont_roe
        
        assert isinstance(dupont, dict)
        assert 'roe' in dupont
        assert 'profit_margin' in dupont
        assert 'asset_turnover' in dupont
        assert 'equity_multiplier' in dupont
        assert 'calculated_roe' in dupont


class TestRatiosIntegration:
    """Test integration of new ratios with existing functionality."""
    
    @pytest.fixture
    def stock(self):
        """Create a stock instance for testing."""
        return Stock("AAPL")
    
    def test_all_ratios_includes_new_metrics(self, stock):
        """Test that all() method includes new ratios."""
        all_ratios = stock.ratios.all()
        
        # Check TTM metrics are included
        assert 'ttm_eps' in all_ratios
        assert 'ttm_pe' in all_ratios
        assert 'ttm_revenue' in all_ratios
        
        # Check advanced ratios are included
        assert 'roic' in all_ratios
        assert 'wacc' in all_ratios
        assert 'equity_multiplier' in all_ratios
    
    def test_profitability_ratios_includes_roic(self, stock):
        """Test that profitability_ratios() includes ROIC."""
        profitability = stock.ratios.profitability_ratios()
        
        assert isinstance(profitability, dict)
        assert 'roic' in profitability
        assert 'roe' in profitability
        assert 'roa' in profitability
    
    def test_leverage_ratios_includes_new_metrics(self, stock):
        """Test that leverage_ratios() includes new metrics."""
        leverage = stock.ratios.leverage_ratios()
        
        assert isinstance(leverage, dict)
        assert 'equity_multiplier' in leverage
        assert 'wacc' in leverage
        assert 'debt_to_equity' in leverage


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_ratios_with_missing_data(self):
        """Test ratios calculation when data is missing."""
        # Use a stock that might have missing data
        stock = Stock("BRK-A")  # Berkshire Hathaway doesn't pay dividends
        
        # Should not raise errors even with missing data
        roic = stock.ratios.roic
        wacc = stock.ratios.wacc
        ttm_eps = stock.ratios.ttm_eps
        
        # Results can be None, but shouldn't error
        assert roic is None or isinstance(roic, (int, float))
        assert wacc is None or isinstance(wacc, (int, float))
        assert ttm_eps is None or isinstance(ttm_eps, (int, float))
    
    def test_ratios_consistency(self):
        """Test that ratios are internally consistent."""
        stock = Stock("AAPL")
        
        # If TTM PE is available, it should equal price / TTM EPS
        ttm_pe = stock.ratios.ttm_pe
        ttm_eps = stock.ratios.ttm_eps
        price = stock.price
        
        if all([ttm_pe, ttm_eps, price]):
            calculated_pe = price / ttm_eps
            # Allow some tolerance for rounding
            assert abs(calculated_pe - ttm_pe) / ttm_pe < 0.1  # Within 10%
