"""Tests for fixed income (Bond) module."""

import pytest

from investormate.finance.bonds import Bond, bond_ladder
from investormate.utils.exceptions import ValidationError


class TestBondPricing:
    def test_price_par_bond(self):
        b = Bond(face=1000, coupon=0.05, ytm=0.05, n=10, frequency=2)
        assert b.price() == pytest.approx(1000, rel=1e-2)

    def test_price_discount_bond(self):
        b = Bond(face=1000, coupon=0.06, ytm=0.05, n=10, frequency=2)
        assert b.price() > 1000

    def test_ytm_roundtrip(self):
        b = Bond(face=1000, coupon=0.06, ytm=0.05, n=10, frequency=2)
        price = b.price()
        solved = Bond(
            face=1000, coupon=0.06, n=10, frequency=2, price=price
        ).solve_ytm()
        assert solved == pytest.approx(0.05, rel=1e-3)

    def test_current_yield(self):
        b = Bond(face=1000, coupon=0.06, ytm=0.05, n=10)
        cy = b.current_yield()
        assert cy == pytest.approx(0.06 * 1000 / b.price(), rel=1e-4)


class TestDurationConvexity:
    def test_duration_positive(self):
        b = Bond(face=1000, coupon=0.06, ytm=0.05, n=10)
        assert b.macaulay_duration() > 0
        assert b.modified_duration() < b.macaulay_duration()

    def test_convexity_positive(self):
        b = Bond(face=1000, coupon=0.06, ytm=0.05, n=10)
        assert b.convexity() > 0

    def test_price_change(self):
        b = Bond(face=1000, coupon=0.06, ytm=0.05, n=10)
        result = b.price_change(0.01)
        assert "total_price_change_pct" in result
        assert result["total_price_change_pct"] < 0


class TestBondLadder:
    def test_bond_ladder_weights(self):
        ladder = bond_ladder([1, 3, 5, 7, 10])
        assert len(ladder) == 5
        assert sum(r["weight"] for r in ladder) == pytest.approx(1.0, rel=1e-3)

    def test_empty_maturities(self):
        with pytest.raises(ValidationError):
            bond_ladder([])
