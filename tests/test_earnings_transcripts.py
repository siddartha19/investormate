"""
Tests for earnings call transcripts functionality.
"""

import pytest
import pandas as pd
from investormate import Stock
from investormate.data import EarningsCallTranscripts


class TestEarningsCallTranscripts:
    """Test earnings call transcripts functionality."""
    
    @pytest.fixture
    def transcripts(self):
        """Create an earnings transcripts instance."""
        return EarningsCallTranscripts("AAPL")
    
    def test_initialization(self, transcripts):
        """Test transcripts object initialization."""
        assert transcripts.ticker == "AAPL"
        assert transcripts._ticker_obj is None  # Lazy loaded
        assert transcripts._transcripts_cache == {}
    
    def test_get_transcripts_list(self, transcripts):
        """Test getting list of available transcripts."""
        transcripts_list = transcripts.get_transcripts_list()
        
        assert isinstance(transcripts_list, pd.DataFrame)
        
        # Check required columns exist
        expected_columns = ['fiscal_year', 'fiscal_quarter', 'report_date', 'has_transcript']
        for col in expected_columns:
            assert col in transcripts_list.columns
    
    def test_get_transcript_returns_none(self, transcripts):
        """Test that get_transcript returns None (yfinance limitation)."""
        transcript = transcripts.get_transcript(2024, 4)
        
        # yfinance doesn't provide transcripts, so should be None
        assert transcript is None
    
    def test_print_pretty_table_handles_none(self, transcripts, capsys):
        """Test that print_pretty_table handles missing transcripts gracefully."""
        transcripts.print_pretty_table(2024, 4)
        
        captured = capsys.readouterr()
        assert "not available" in captured.out.lower()
    
    def test_search_transcript_empty_result(self, transcripts):
        """Test searching when transcript is not available."""
        matches = transcripts.search_transcript(2024, 4, "revenue")
        
        assert isinstance(matches, list)
        assert len(matches) == 0  # No matches since no transcript
    
    def test_get_all_transcripts(self, transcripts):
        """Test getting all transcripts."""
        all_transcripts = transcripts.get_all_transcripts()
        
        assert isinstance(all_transcripts, dict)
        # Should be empty since yfinance doesn't provide transcripts
        # But should not error


class TestStockIntegration:
    """Test earnings transcripts integration with Stock class."""
    
    @pytest.fixture
    def stock(self):
        """Create a stock instance."""
        return Stock("AAPL")
    
    def test_stock_has_earnings_transcripts_property(self, stock):
        """Test that Stock has earnings_transcripts property."""
        assert hasattr(stock, 'earnings_transcripts')
    
    def test_earnings_transcripts_returns_correct_type(self, stock):
        """Test that earnings_transcripts returns EarningsCallTranscripts."""
        transcripts = stock.earnings_transcripts
        
        assert isinstance(transcripts, EarningsCallTranscripts)
        assert transcripts.ticker == stock.ticker
    
    def test_earnings_transcripts_cached(self, stock):
        """Test that earnings_transcripts is cached."""
        transcripts1 = stock.earnings_transcripts
        transcripts2 = stock.earnings_transcripts
        
        assert transcripts1 is transcripts2  # Same object
    
    def test_refresh_clears_transcripts_cache(self, stock):
        """Test that refresh() clears transcripts cache."""
        transcripts1 = stock.earnings_transcripts
        stock.refresh()
        transcripts2 = stock.earnings_transcripts
        
        assert transcripts1 is not transcripts2  # Different objects


class TestTranscriptsDataStructure:
    """Test expected data structures for transcripts."""
    
    def test_transcripts_list_structure(self):
        """Test structure of transcripts list DataFrame."""
        transcripts = EarningsCallTranscripts("AAPL")
        df = transcripts.get_transcripts_list()
        
        if not df.empty:
            # Check data types
            assert df['fiscal_year'].dtype in [int, 'int64']
            assert df['fiscal_quarter'].dtype in [int, 'int64']
            assert df['report_date'].dtype in [object, 'string']
            assert df['has_transcript'].dtype == bool
            
            # Check value ranges
            assert all(df['fiscal_quarter'].between(1, 4))
            assert all(df['fiscal_year'] >= 2000)
    
    def test_transcript_structure_when_available(self):
        """Test expected structure of transcript DataFrame."""
        # This is a placeholder test for when transcripts become available
        # Expected columns would be: paragraph_number, speaker, content
        
        # Mock transcript data structure
        expected_columns = ['paragraph_number', 'speaker', 'content']
        
        # This test documents the expected structure
        assert len(expected_columns) == 3
        assert 'paragraph_number' in expected_columns
        assert 'speaker' in expected_columns
        assert 'content' in expected_columns


class TestErrorHandling:
    """Test error handling for transcripts."""
    
    def test_invalid_ticker_handling(self):
        """Test handling of invalid ticker."""
        # Should not error during initialization
        transcripts = EarningsCallTranscripts("INVALID_TICKER_XYZ")
        assert transcripts.ticker == "INVALID_TICKER_XYZ"
        
        # May error or return empty when fetching data
        try:
            transcripts_list = transcripts.get_transcripts_list()
            assert isinstance(transcripts_list, pd.DataFrame)
        except Exception:
            pass  # Expected for invalid ticker
    
    def test_invalid_quarter(self):
        """Test handling of invalid quarter number."""
        transcripts = EarningsCallTranscripts("AAPL")
        
        # Should handle invalid quarters gracefully
        transcript = transcripts.get_transcript(2024, 5)  # Invalid quarter
        assert transcript is None
    
    def test_future_year(self):
        """Test handling of future year."""
        transcripts = EarningsCallTranscripts("AAPL")
        
        # Should handle future years gracefully
        transcript = transcripts.get_transcript(2030, 1)
        assert transcript is None
