"""Tests for full Beneish M-Score (eight-variable model)."""

import pytest

from investormate.analysis.scores import (
    FinancialScores,
    _beneish_compute_indices,
    _beneish_m_from_indices,
)


def test_beneish_m_from_indices_all_ones():
    indices = {
        "DSRI": 1.0,
        "GMI": 1.0,
        "AQI": 1.0,
        "SGI": 1.0,
        "DEPI": 1.0,
        "SGAI": 1.0,
        "TATA": 0.0,
        "LVGI": 1.0,
    }
    m = _beneish_m_from_indices(indices)
    # -4.84 + 0.920 + 0.528 + 0.404 + 0.892 + 0.115 - 0.172 - 0.327
    expected = -4.84 + 0.920 + 0.528 + 0.404 + 0.892 + 0.115 - 0.172 - 0.327
    assert pytest.approx(m, rel=1e-9) == expected


def test_beneish_compute_indices_two_periods():
    t, tm1 = "2024-09-30", "2023-09-30"
    balance_sheet = {
        t: {
            "Accounts Receivable": 100.0,
            "Total Current Assets": 400.0,
            "Net PPE": 300.0,
            "Total Assets": 1000.0,
            "Total Liabilities Net Minority Interest": 400.0,
        },
        tm1: {
            "Accounts Receivable": 80.0,
            "Total Current Assets": 380.0,
            "Net PPE": 320.0,
            "Total Assets": 950.0,
            "Total Liabilities Net Minority Interest": 380.0,
        },
    }
    income_stmt = {
        t: {
            "Total Revenue": 500.0,
            "Cost Of Revenue": 300.0,
            "Reconciled Depreciation": 40.0,
            "Selling General And Administration": 50.0,
            "Net Income": 60.0,
        },
        tm1: {
            "Total Revenue": 450.0,
            "Cost Of Revenue": 270.0,
            "Reconciled Depreciation": 35.0,
            "Selling General And Administration": 45.0,
            "Net Income": 55.0,
        },
    }
    cash_flow = {
        t: {"Operating Cash Flow": 70.0},
        tm1: {"Operating Cash Flow": 65.0},
    }

    indices, err = _beneish_compute_indices(balance_sheet, income_stmt, cash_flow)
    assert err == ""
    assert indices is not None
    assert set(indices.keys()) == {
        "DSRI",
        "GMI",
        "AQI",
        "SGI",
        "DEPI",
        "SGAI",
        "TATA",
        "LVGI",
    }
    assert indices["SGI"] == pytest.approx(500.0 / 450.0)
    m = _beneish_m_from_indices(indices)
    assert isinstance(m, float)


def test_financial_scores_beneish_detail_and_fallback():
    info = {
        "totalRevenue": 1e9,
        "totalAssets": 5e9,
        "debtToEquity": 50.0,
        "grossMargins": 0.40,
    }
    # No statements -> detail score None, tuple uses proxy
    scores = FinancialScores(info, {}, {}, {})
    detail = scores.beneish_m_score_detail()
    assert detail["score"] is None
    m, interp = scores.beneish_m_score()
    assert m is not None
    assert "proxy" in interp.lower() or "Low risk" in interp
