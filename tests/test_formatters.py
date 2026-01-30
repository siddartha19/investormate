"""
Tests for formatting utilities.
"""

import pytest
import pandas as pd
from investormate.utils.formatters import (
    format_number,
    format_large_number,
    format_percentage,
    format_currency,
    print_financial_statement,
    print_ratios_table,
    print_comparison_table,
    print_dataframe_pretty,
)


class TestNumberFormatting:
    """Test number formatting functions."""
    
    def test_format_number_basic(self):
        """Test basic number formatting."""
        assert format_number(1234.567, decimals=2) == "1,234.57"
        assert format_number(1234.567, decimals=0) == "1,235"
        assert format_number(1000000, decimals=0) == "1,000,000"
    
    def test_format_number_with_prefix_suffix(self):
        """Test number formatting with prefix and suffix."""
        assert format_number(123.45, prefix="$") == "$123.45"
        assert format_number(0.15, decimals=1, suffix="%") == "0.1%"
        assert format_number(100, prefix="$", suffix=" USD") == "$100.00 USD"
    
    def test_format_number_none_value(self):
        """Test formatting None values."""
        assert format_number(None) == "N/A"
        assert format_number(pd.NA) == "N/A"
    
    def test_format_large_number(self):
        """Test large number formatting with suffixes."""
        assert format_large_number(1500) == "1.50K"
        assert format_large_number(1500000) == "1.50M"
        assert format_large_number(1500000000) == "1.50B"
        assert format_large_number(1500000000000) == "1.50T"
    
    def test_format_large_number_small(self):
        """Test large number formatting with small values."""
        assert format_large_number(500) == "500.00"
        assert format_large_number(50.5) == "50.50"
    
    def test_format_large_number_none(self):
        """Test large number formatting with None."""
        assert format_large_number(None) == "N/A"
    
    def test_format_percentage(self):
        """Test percentage formatting."""
        assert format_percentage(0.15) == "15.00%"
        assert format_percentage(0.1234, decimals=1) == "12.3%"
        assert format_percentage(1.0) == "100.00%"
        assert format_percentage(-0.05) == "-5.00%"
    
    def test_format_percentage_none(self):
        """Test percentage formatting with None."""
        assert format_percentage(None) == "N/A"
    
    def test_format_currency(self):
        """Test currency formatting."""
        assert format_currency(1234.56) == "$1,234.56"
        assert format_currency(1000000, decimals=0) == "$1,000,000"
        assert format_currency(99.99, currency="€") == "€99.99"


class TestPrintFunctions:
    """Test print functions."""
    
    def test_print_financial_statement(self, capsys):
        """Test printing financial statement."""
        data = {
            '2024-12-31': {
                'Revenue': 100000000,
                'Net Income': 25000000,
            },
            '2023-12-31': {
                'Revenue': 90000000,
                'Net Income': 20000000,
            }
        }
        
        print_financial_statement(data, title="Test Statement")
        captured = capsys.readouterr()
        
        assert "Test Statement" in captured.out
        assert "Revenue" in captured.out
        assert "Net Income" in captured.out
    
    def test_print_financial_statement_empty(self, capsys):
        """Test printing empty financial statement."""
        print_financial_statement({}, title="Empty Statement")
        captured = capsys.readouterr()
        
        assert "No data available" in captured.out
    
    def test_print_ratios_table(self, capsys):
        """Test printing ratios table."""
        ratios = {
            'pe': 25.5,
            'roe': 0.15,
            'debt_to_equity': 1.2,
            'current_ratio': 1.5,
        }
        
        print_ratios_table(ratios, title="Test Ratios")
        captured = capsys.readouterr()
        
        assert "Test Ratios" in captured.out
        assert "Valuation" in captured.out or "pe" in captured.out.lower()
    
    def test_print_ratios_table_empty(self, capsys):
        """Test printing empty ratios table."""
        print_ratios_table({}, title="Empty Ratios")
        captured = capsys.readouterr()
        
        assert "No data available" in captured.out
    
    def test_print_comparison_table(self, capsys):
        """Test printing comparison table."""
        stocks = ["AAPL", "MSFT", "GOOGL"]
        metrics = {
            'Price': {'AAPL': 150.0, 'MSFT': 300.0, 'GOOGL': 140.0},
            'P/E Ratio': {'AAPL': 25.0, 'MSFT': 30.0, 'GOOGL': 22.0},
        }
        
        print_comparison_table(stocks, metrics, title="Stock Comparison")
        captured = capsys.readouterr()
        
        assert "Stock Comparison" in captured.out
        assert "AAPL" in captured.out
        assert "Price" in captured.out
    
    def test_print_comparison_table_empty(self, capsys):
        """Test printing empty comparison table."""
        print_comparison_table([], {}, title="Empty Comparison")
        captured = capsys.readouterr()
        
        assert "No data available" in captured.out
    
    def test_print_dataframe_pretty(self, capsys):
        """Test pretty printing DataFrame."""
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4.5, 5.5, 6.5],
            'C': ['x', 'y', 'z']
        })
        
        print_dataframe_pretty(df, title="Test DataFrame")
        captured = capsys.readouterr()
        
        assert "Test DataFrame" in captured.out
        assert "A" in captured.out
        assert "B" in captured.out
    
    def test_print_dataframe_pretty_empty(self, capsys):
        """Test pretty printing empty DataFrame."""
        df = pd.DataFrame()
        print_dataframe_pretty(df)
        captured = capsys.readouterr()
        
        assert "No data available" in captured.out
    
    def test_print_dataframe_pretty_none(self, capsys):
        """Test pretty printing None."""
        print_dataframe_pretty(None)
        captured = capsys.readouterr()
        
        assert "No data available" in captured.out


class TestEdgeCases:
    """Test edge cases in formatting."""
    
    def test_format_number_negative(self):
        """Test formatting negative numbers."""
        assert format_number(-1234.56) == "-1,234.56"
        assert format_large_number(-1000000) == "-1.00M"
        assert format_percentage(-0.05) == "-5.00%"
    
    def test_format_number_zero(self):
        """Test formatting zero."""
        assert format_number(0) == "0.00"
        assert format_large_number(0) == "0.00"
        assert format_percentage(0) == "0.00%"
    
    def test_format_number_very_large(self):
        """Test formatting very large numbers."""
        assert "T" in format_large_number(5000000000000)
        assert "," in format_number(1000000000000)
    
    def test_format_number_very_small(self):
        """Test formatting very small numbers."""
        assert format_number(0.001, decimals=3) == "0.001"
        assert format_percentage(0.0001, decimals=4) == "0.0100%"
