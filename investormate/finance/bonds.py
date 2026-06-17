"""
Fixed income analytics for InvestorMate.

Pure math bond pricing — no FRED/yield-curve dependency in v0.5.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union

import numpy as np

from ..utils.exceptions import ValidationError


def _parse_date(value: Union[str, date, datetime]) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.strptime(value[:10], "%Y-%m-%d").date()
    raise ValidationError(
        "settlement_date must be a date, datetime, or YYYY-MM-DD string"
    )


class Bond:
    """
    Fixed-rate bond analytics (clean price, YTM, duration, convexity).

    Example:
        >>> b = Bond(face=1000, coupon=0.06, ytm=0.05, n=10, frequency=2)
        >>> b.price()
        >>> b.modified_duration()
    """

    def __init__(
        self,
        face: float = 1000.0,
        coupon: float = 0.06,
        ytm: Optional[float] = None,
        n: int = 10,
        *,
        frequency: int = 2,
        price: Optional[float] = None,
    ):
        if face <= 0:
            raise ValidationError("face must be positive")
        if n <= 0:
            raise ValidationError("n must be positive")
        if frequency <= 0:
            raise ValidationError("frequency must be positive")
        self.face = float(face)
        self.coupon = float(coupon)
        self._annual_ytm = float(ytm) if ytm is not None else None
        self.n = int(n)
        self.frequency = int(frequency)
        self._price = float(price) if price is not None else None

    @property
    def ytm(self) -> Optional[float]:
        """Annual yield to maturity used for pricing (if set)."""
        return self._annual_ytm

    @ytm.setter
    def ytm(self, value: Optional[float]) -> None:
        self._annual_ytm = float(value) if value is not None else None

    def _coupon_payment(self) -> float:
        return self.face * self.coupon / self.frequency

    def _cash_flows(self) -> List[float]:
        c = self._coupon_payment()
        flows = [c] * (self.n * self.frequency)
        flows[-1] += self.face
        return flows

    def _periodic_ytm(self, ytm: Optional[float] = None) -> float:
        y = self._annual_ytm if ytm is None else float(ytm)
        if y is None:
            raise ValidationError("ytm must be set for this calculation")
        return y / self.frequency

    def price(self, ytm: Optional[float] = None) -> float:
        """Clean price from yield to maturity."""
        y = self._annual_ytm if ytm is None else float(ytm)
        y_p = y / self.frequency
        c = self._coupon_payment()
        periods = self.n * self.frequency
        if y_p == 0:
            return float(c * periods + self.face)
        pv_coupons = c * (1 - (1 + y_p) ** (-periods)) / y_p
        pv_face = self.face / ((1 + y_p) ** periods)
        return float(pv_coupons + pv_face)

    def current_yield(self, market_price: Optional[float] = None) -> float:
        """Annual coupon / market price."""
        p = market_price if market_price is not None else self._price
        if p is None:
            p = self.price()
        if p <= 0:
            raise ValidationError("market price must be positive")
        return float(self.face * self.coupon / p)

    def solve_ytm(
        self,
        price: Optional[float] = None,
        *,
        guess: float = 0.05,
        tol: float = 1e-8,
        max_iter: int = 100,
    ) -> float:
        """Solve for YTM given clean price (bisection)."""
        target = price if price is not None else self._price
        if target is None:
            raise ValidationError("price must be provided to solve for ytm")

        def _price_at(annual_ytm: float) -> float:
            return Bond(
                face=self.face,
                coupon=self.coupon,
                ytm=annual_ytm,
                n=self.n,
                frequency=self.frequency,
            ).price()

        low, high = -0.5, 1.0
        f_low = _price_at(low) - target
        f_high = _price_at(high) - target
        expand = 0
        while f_low * f_high > 0 and expand < 15:
            high *= 1.5
            f_high = _price_at(high) - target
            expand += 1
        if f_low * f_high > 0:
            raise ValidationError("YTM could not be bracketed for the given price")

        for _ in range(max_iter):
            mid = (low + high) / 2
            f_mid = _price_at(mid) - target
            if abs(f_mid) < tol or (high - low) / 2 < tol:
                return float(mid)
            if f_low * f_mid <= 0:
                high, f_high = mid, f_mid
            else:
                low, f_low = mid, f_mid
        return float((low + high) / 2)

    def accrued_interest(
        self,
        settlement_date: Union[str, date, datetime],
        *,
        last_coupon_date: Optional[Union[str, date, datetime]] = None,
        days_in_period: int = 180,
    ) -> float:
        """
        Accrued interest between last coupon and settlement (30/360 style default).
        """
        settle = _parse_date(settlement_date)
        if last_coupon_date is None:
            # Assume settlement is `days_since` into a 6-month period
            days_since = min(days_in_period - 1, max(0, settle.day))
        else:
            last = _parse_date(last_coupon_date)
            days_since = (settle - last).days
            if days_since < 0:
                raise ValidationError("settlement_date must be after last_coupon_date")
        coupon = self._coupon_payment()
        return float(coupon * days_since / days_in_period)

    def macaulay_duration(self, ytm: Optional[float] = None) -> float:
        """Macaulay duration in years."""
        y = self._annual_ytm if ytm is None else float(ytm)
        if y is None:
            raise ValidationError("ytm must be set for this calculation")
        y_p = y / self.frequency
        c = self._coupon_payment()
        periods = self.n * self.frequency
        weighted = 0.0
        pv_total = 0.0
        for t in range(1, periods + 1):
            cf = c + (self.face if t == periods else 0.0)
            pv = cf / ((1 + y_p) ** t)
            weighted += t * pv
            pv_total += pv
        if pv_total == 0:
            return 0.0
        return float(weighted / pv_total / self.frequency)

    def modified_duration(self, ytm: Optional[float] = None) -> float:
        """Modified duration = Macaulay / (1 + y/frequency)."""
        y = self._annual_ytm if ytm is None else float(ytm)
        if y is None:
            raise ValidationError("ytm must be set for this calculation")
        mac = self.macaulay_duration(ytm=y)
        return float(mac / (1 + y / self.frequency))

    def convexity(self, ytm: Optional[float] = None) -> float:
        """Convexity measure (annualized)."""
        y = self._annual_ytm if ytm is None else float(ytm)
        if y is None:
            raise ValidationError("ytm must be set for this calculation")
        y_p = y / self.frequency
        c = self._coupon_payment()
        periods = self.n * self.frequency
        conv = 0.0
        pv_total = 0.0
        for t in range(1, periods + 1):
            cf = c + (self.face if t == periods else 0.0)
            pv = cf / ((1 + y_p) ** t)
            conv += t * (t + 1) * pv
            pv_total += pv
        if pv_total == 0:
            return 0.0
        return float(conv / (pv_total * (1 + y_p) ** 2) / (self.frequency**2))

    def price_change(
        self, yield_change: float, ytm: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Approximate price change using duration and convexity.

        %ΔP ≈ -ModDur * Δy + 0.5 * Convexity * (Δy)^2
        """
        y = self._annual_ytm if ytm is None else float(ytm)
        if y is None:
            raise ValidationError("ytm must be set for this calculation")
        mod_dur = self.modified_duration(ytm=y)
        conv = self.convexity(ytm=y)
        dy = float(yield_change)
        duration_effect = -mod_dur * dy
        convexity_effect = 0.5 * conv * (dy**2)
        total_pct = duration_effect + convexity_effect
        return {
            "yield_change": dy,
            "duration_effect_pct": float(duration_effect),
            "convexity_effect_pct": float(convexity_effect),
            "total_price_change_pct": float(total_pct),
            "modified_duration": mod_dur,
            "convexity": conv,
        }


def bond_ladder(
    maturities: List[int],
    *,
    face_per_bond: float = 1000.0,
    coupon: float = 0.05,
    ytm: float = 0.05,
    frequency: int = 2,
) -> List[Dict[str, Any]]:
    """
    Build a simple maturity ladder with equal face per maturity.

    Returns list of dicts with maturity, price, macaulay_duration, weight.
    """
    if not maturities:
        raise ValidationError("maturities must be a non-empty list")
    bonds = []
    total_value = 0.0
    for m in maturities:
        b = Bond(
            face=face_per_bond, coupon=coupon, ytm=ytm, n=int(m), frequency=frequency
        )
        p = b.price()
        bonds.append(
            {
                "maturity_years": int(m),
                "face": face_per_bond,
                "price": round(p, 2),
                "macaulay_duration": round(b.macaulay_duration(), 4),
            }
        )
        total_value += p
    for row in bonds:
        row["weight"] = round(row["price"] / total_value, 4) if total_value else 0.0
    return bonds
