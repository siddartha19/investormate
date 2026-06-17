"""
Time Value of Money (TVM) calculations for InvestorMate.

Pure numpy/pandas math — no market data required.
"""

from typing import List, Optional, Union

import numpy as np
import pandas as pd

from ..utils.exceptions import ValidationError


def _validate_rate(rate: float, name: str = "rate") -> float:
    if rate is None:
        raise ValidationError(f"{name} must be provided")
    try:
        r = float(rate)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{name} must be a number") from exc
    if r <= -1:
        raise ValidationError(f"{name} must be greater than -1")
    return r


def _validate_periods(n: int, name: str = "n") -> int:
    try:
        periods = int(n)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{name} must be a positive integer") from exc
    if periods <= 0:
        raise ValidationError(f"{name} must be a positive integer")
    return periods


def present_value(
    fv: float,
    rate: float,
    n: int,
) -> float:
    """
    Present value of a lump sum.

    PV = FV / (1 + r)^n
    """
    r = _validate_rate(rate)
    periods = _validate_periods(n)
    return float(fv / ((1 + r) ** periods))


def future_value(
    pv: float,
    rate: float,
    n: int,
) -> float:
    """
    Future value of a lump sum.

    FV = PV * (1 + r)^n
    """
    r = _validate_rate(rate)
    periods = _validate_periods(n)
    return float(pv * ((1 + r) ** periods))


def annuity_pv(
    pmt: float,
    rate: float,
    n: int,
    *,
    due: bool = False,
) -> float:
    """
    Present value of an annuity (ordinary or annuity due).

    Ordinary: PV = PMT * [1 - (1+r)^-n] / r
    Due: multiply by (1 + r)
    """
    r = _validate_rate(rate)
    periods = _validate_periods(n)
    if r == 0:
        pv = pmt * periods
    else:
        pv = pmt * (1 - (1 + r) ** (-periods)) / r
    if due:
        pv *= 1 + r
    return float(pv)


def annuity_fv(
    pmt: float,
    rate: float,
    n: int,
    *,
    due: bool = False,
) -> float:
    """
    Future value of an annuity (ordinary or annuity due).
    """
    r = _validate_rate(rate)
    periods = _validate_periods(n)
    if r == 0:
        fv = pmt * periods
    else:
        fv = pmt * (((1 + r) ** periods - 1) / r)
    if due:
        fv *= 1 + r
    return float(fv)


def perpetuity(
    pmt: float,
    rate: float,
    *,
    growth: Optional[float] = None,
) -> float:
    """
    Present value of a level or growing perpetuity.

    Level: PV = PMT / r
    Growing (Gordon): PV = PMT / (r - g), requires r > g
    """
    r = _validate_rate(rate)
    if growth is None:
        if r == 0:
            raise ValidationError("rate must be positive for a level perpetuity")
        return float(pmt / r)
    g = float(growth)
    if r <= g:
        raise ValidationError(
            "rate must be greater than growth for a growing perpetuity"
        )
    return float(pmt / (r - g))


def npv(rate: float, cashflows: List[float]) -> float:
    """
    Net present value of uneven cash flows (CF0 at t=0).
    """
    r = _validate_rate(rate)
    if not cashflows:
        raise ValidationError("cashflows must be a non-empty list")
    total = 0.0
    for t, cf in enumerate(cashflows):
        total += float(cf) / ((1 + r) ** t)
    return float(total)


def irr(
    cashflows: List[float],
    *,
    guess: float = 0.1,
    tol: float = 1e-8,
    max_iter: int = 100,
) -> float:
    """
    Internal rate of return for uneven cash flows (bisection with bracket search).
    """
    if not cashflows or len(cashflows) < 2:
        raise ValidationError("cashflows must contain at least two values")

    cfs = [float(c) for c in cashflows]
    if all(c >= 0 for c in cfs) or all(c <= 0 for c in cfs):
        raise ValidationError(
            "cashflows must include both positive and negative values"
        )

    def _npv_at(rate: float) -> float:
        return sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cfs))

    # Try Newton-Raphson first
    rate = guess
    for _ in range(max_iter):
        f = _npv_at(rate)
        # derivative of NPV w.r.t. rate
        df = sum(-t * cf / ((1 + rate) ** (t + 1)) for t, cf in enumerate(cfs) if t > 0)
        if abs(df) < 1e-12:
            break
        step = f / df
        rate_new = rate - step
        if abs(rate_new - rate) < tol:
            return float(rate_new)
        rate = rate_new

    # Bisection fallback on a wide bracket
    low, high = -0.99, 10.0
    f_low, f_high = _npv_at(low), _npv_at(high)
    expand = 0
    while f_low * f_high > 0 and expand < 20:
        high *= 2
        f_high = _npv_at(high)
        expand += 1
    if f_low * f_high > 0:
        raise ValidationError("IRR could not be bracketed for the given cashflows")

    for _ in range(max_iter):
        mid = (low + high) / 2
        f_mid = _npv_at(mid)
        if abs(f_mid) < tol or (high - low) / 2 < tol:
            return float(mid)
        if f_low * f_mid <= 0:
            high, f_high = mid, f_mid
        else:
            low, f_low = mid, f_mid
    return float((low + high) / 2)


def amortization_schedule(
    principal: float,
    rate: float,
    n: int,
    *,
    periods_per_year: int = 12,
) -> pd.DataFrame:
    """
    Loan amortization schedule with payment, interest, principal, and balance.

    Args:
        principal: Loan amount
        rate: Annual nominal interest rate (e.g. 0.04 for 4%)
        n: Number of years
        periods_per_year: Payments per year (12 for monthly)
    """
    if principal <= 0:
        raise ValidationError("principal must be positive")
    years = _validate_periods(n)
    freq = _validate_periods(periods_per_year, name="periods_per_year")
    total_periods = years * freq
    periodic_rate = rate / freq if rate != 0 else 0.0

    if periodic_rate == 0:
        payment = principal / total_periods
    else:
        payment = (
            principal
            * (periodic_rate * (1 + periodic_rate) ** total_periods)
            / ((1 + periodic_rate) ** total_periods - 1)
        )

    rows = []
    balance = float(principal)
    for period in range(1, total_periods + 1):
        interest = balance * periodic_rate
        principal_paid = payment - interest
        balance = max(0.0, balance - principal_paid)
        rows.append(
            {
                "period": period,
                "payment": round(payment, 2),
                "interest": round(interest, 2),
                "principal": round(principal_paid, 2),
                "balance": round(balance, 2),
            }
        )

    return pd.DataFrame(rows)


def ear(
    nominal: float,
    compounding: int = 12,
) -> float:
    """
    Effective annual rate from nominal rate and compounding frequency.

    EAR = (1 + nominal/m)^m - 1
    """
    r = _validate_rate(nominal, name="nominal")
    m = _validate_periods(compounding, name="compounding")
    return float((1 + r / m) ** m - 1)
