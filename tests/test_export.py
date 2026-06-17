"""Tests for report/export utilities."""

import pytest
from unittest.mock import patch, MagicMock

from investormate import Stock
from investormate.reporting.export import markdown_report, export_to_excel
from investormate.utils.exceptions import ValidationError


class TestExport:
    def test_markdown_report(self):
        md = markdown_report(
            "AAPL",
            "Apple Inc.",
            {"currentPrice": 150, "sector": "Technology"},
            {"pe": 25, "roe": 0.15, "current_ratio": 1.5},
        )
        assert "# Apple Inc." in md
        assert "P/E" in md

    def test_export_to_excel_requires_openpyxl(self, tmp_path, monkeypatch):
        import builtins

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "openpyxl":
                raise ImportError("mocked missing openpyxl")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)
        with pytest.raises(ValidationError, match="openpyxl"):
            export_to_excel(
                str(tmp_path / "out.xlsx"),
                ticker="TEST",
                info={},
                ratios={"pe": 10},
            )

    @patch("investormate.core.stock.get_data_provider")
    def test_stock_report(self, mock_provider):
        mock_provider.return_value.get_info.return_value = {
            "shortName": "Test Co",
            "currentPrice": 100,
            "sector": "Tech",
            "trailingPE": 20,
            "returnOnEquity": 0.1,
            "currentRatio": 1.5,
        }
        mock_provider.return_value.get_balance_sheet.return_value = {}
        mock_provider.return_value.get_income_statement.return_value = {}
        mock_provider.return_value.get_cash_flow.return_value = {}
        stock = Stock("TEST")
        md = stock.report()
        assert "Test Co" in md
