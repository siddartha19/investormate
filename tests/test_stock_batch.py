"""Tests for Stock.batch."""

import pytest

from investormate import Stock


def test_batch_skip_invalid():
    with pytest.warns(UserWarning, match="Skipping ticker"):
        stocks = Stock.batch(["AAPL", ""], skip_invalid=True)
    assert len(stocks) == 1
    assert stocks[0].ticker == "AAPL"


def test_batch_raises_when_not_skipping():
    with pytest.raises(Exception):
        Stock.batch(["AAPL", ""], skip_invalid=False)


def test_batch_multiple_valid():
    stocks = Stock.batch(["MSFT", "GOOGL"], skip_invalid=True)
    assert len(stocks) == 2
    assert {s.ticker for s in stocks} == {"MSFT", "GOOGL"}
