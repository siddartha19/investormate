"""Tests for TVM module."""

import math

import pytest

from investormate.finance import tvm
from investormate.utils.exceptions import ValidationError


class TestPresentFutureValue:
    def test_present_value(self):
        assert tvm.present_value(1000, 0.05, 10) == pytest.approx(613.91, rel=1e-3)

    def test_future_value(self):
        assert tvm.future_value(500, 0.08, 5) == pytest.approx(734.66, rel=1e-3)

    def test_invalid_rate(self):
        with pytest.raises(ValidationError):
            tvm.present_value(100, -1.5, 5)


class TestAnnuities:
    def test_annuity_pv_ordinary(self):
        assert tvm.annuity_pv(100, 0.08, 20) == pytest.approx(981.81, rel=1e-2)

    def test_annuity_pv_due(self):
        ordinary = tvm.annuity_pv(100, 0.08, 20, due=False)
        due = tvm.annuity_pv(100, 0.08, 20, due=True)
        assert due == pytest.approx(ordinary * 1.08, rel=1e-6)

    def test_annuity_fv(self):
        assert tvm.annuity_fv(100, 0.08, 10) == pytest.approx(1448.66, rel=1e-2)

    def test_perpetuity_level(self):
        assert tvm.perpetuity(50, 0.05) == pytest.approx(1000.0)

    def test_perpetuity_growing(self):
        # First payment next period: PV = PMT / (r - g)
        assert tvm.perpetuity(50, 0.08, growth=0.02) == pytest.approx(833.33, rel=1e-2)

    def test_perpetuity_growth_error(self):
        with pytest.raises(ValidationError):
            tvm.perpetuity(50, 0.05, growth=0.06)


class TestNPVIRR:
    def test_npv(self):
        cfs = [-1000, 300, 400, 500]
        assert tvm.npv(0.10, cfs) == pytest.approx(-21.04, rel=1e-2)

    def test_irr(self):
        cfs = [-1000, 300, 400, 500]
        rate = tvm.irr(cfs)
        assert rate == pytest.approx(0.0886, rel=1e-2)
        assert tvm.npv(rate, cfs) == pytest.approx(0, abs=1e-4)

    def test_irr_invalid_cashflows(self):
        with pytest.raises(ValidationError):
            tvm.irr([100, 200, 300])


class TestAmortization:
    def test_amortization_schedule_shape(self):
        df = tvm.amortization_schedule(100000, 0.04, 30, periods_per_year=12)
        assert len(df) == 360
        assert df.iloc[-1]["balance"] == pytest.approx(0, abs=1)
        assert df["payment"].iloc[0] == df["payment"].iloc[-1]

    def test_ear(self):
        assert tvm.ear(0.08, 12) == pytest.approx(0.083, rel=1e-2)
