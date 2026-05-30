"""Tests for Investor.batch_analyze threading semantics (order + error capture)."""

from investormate.core.investor import Investor


def _make_investor():
    # Bypass __init__ (which needs API keys); batch_analyze only uses self.ask
    return object.__new__(Investor)


def test_batch_analyze_preserves_input_order():
    inv = _make_investor()
    inv.ask = lambda ticker, question, provider=None: {"answer": f"{ticker}:{question}"}

    queries = [("AAPL", "q1"), ("MSFT", "q2"), ("GOOGL", "q3")]
    results = inv.batch_analyze(queries, max_workers=3)

    assert [r["ticker"] for r in results] == ["AAPL", "MSFT", "GOOGL"]
    assert results[1]["result"]["answer"] == "MSFT:q2"


def test_batch_analyze_captures_per_query_errors():
    inv = _make_investor()

    def fake_ask(ticker, question, provider=None):
        if ticker == "BAD":
            raise ValueError("boom")
        return {"answer": "ok"}

    inv.ask = fake_ask
    results = inv.batch_analyze([("BAD", "q"), ("AAPL", "q")])

    assert results[0]["error"] == "boom"
    assert results[1]["result"] == {"answer": "ok"}


def test_batch_analyze_empty():
    inv = _make_investor()
    inv.ask = lambda *a, **k: {}
    assert inv.batch_analyze([]) == []


def test_batch_analyze_sequential_path():
    inv = _make_investor()
    inv.ask = lambda ticker, question, provider=None: {"t": ticker}
    results = inv.batch_analyze([("AAPL", "q")], max_workers=1)
    assert results == [{"ticker": "AAPL", "question": "q", "result": {"t": "AAPL"}}]
