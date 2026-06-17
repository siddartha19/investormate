"""Tests for options / derivatives module."""

import pytest

from investormate.finance import options
from investormate.utils.exceptions import ValidationError


# Reference: S=100, K=100, T=1, r=0.05, sigma=0.2 -> call ~10.45
class TestBlackScholes:
    def test_call_price(self):
        price = options.black_scholes(100, 100, 1, 0.05, 0.2, "call")
        assert price == pytest.approx(10.45, rel=1e-2)

    def test_put_price(self):
        price = options.black_scholes(100, 100, 1, 0.05, 0.2, "put")
        assert price == pytest.approx(5.57, rel=1e-2)

    def test_put_call_parity(self):
        S, K, T, r, sigma = 100, 100, 1, 0.05, 0.2
        c = options.black_scholes(S, K, T, r, sigma, "call")
        p = options.black_scholes(S, K, T, r, sigma, "put")
        result = options.put_call_parity(c, p, S, K, r, T, tolerance=0.05)
        assert result["holds"] is True


class TestGreeks:
    def test_greeks_keys(self):
        g = options.greeks(150, 155, 0.5, 0.05, 0.25, "call")
        assert "delta" in g
        assert "gamma" in g
        assert "theta" in g
        assert "vega" in g
        assert "rho" in g
        assert 0 < g["delta"] < 1


class TestBinomial:
    def test_binomial_converges_to_bs(self):
        S, K, T, r, sigma = 100, 100, 1, 0.05, 0.2
        bs = options.black_scholes(S, K, T, r, sigma, "call")
        tree = options.binomial(S, K, T, r, sigma, steps=50, option_type="call")
        assert tree["price"] == pytest.approx(bs, rel=0.02)


class TestPayoff:
    def test_covered_call_metrics(self):
        m = options.strategy_metrics("covered_call", S=150, K=160, premium=5)
        assert m["max_profit"] == pytest.approx(15)
        assert m["breakeven"] == pytest.approx(145)

    def test_payoff_diagram(self):
        legs = [
            {
                "type": "call",
                "position": "long",
                "strike": 100,
                "premium": 5,
                "quantity": 1,
            },
            {
                "type": "call",
                "position": "short",
                "strike": 110,
                "premium": 2,
                "quantity": 1,
            },
        ]
        d = options.payoff_diagram("bull_call_spread", legs)
        assert len(d["spot_prices"]) == len(d["payoffs"])

    def test_invalid_strategy(self):
        with pytest.raises(ValidationError):
            options.strategy_metrics("unknown_strategy", S=100)
