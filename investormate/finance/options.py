"""
Derivatives basics for InvestorMate (Black-Scholes, Greeks, binomial tree).

Pure math — no market data required.
"""

import math
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import numpy as np

from ..utils.exceptions import ValidationError

OptionType = Literal["call", "put"]


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def _validate_bs_inputs(S: float, K: float, T: float, r: float, sigma: float) -> None:
    if S <= 0 or K <= 0:
        raise ValidationError("S and K must be positive")
    if T < 0:
        raise ValidationError("T must be non-negative")
    if sigma < 0:
        raise ValidationError("sigma must be non-negative")


def black_scholes(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: OptionType = "call",
) -> float:
    """
    European Black-Scholes option price.
    """
    _validate_bs_inputs(S, K, T, r, sigma)
    if T == 0 or sigma == 0:
        intrinsic = max(S - K, 0.0) if option_type == "call" else max(K - S, 0.0)
        return float(intrinsic)

    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if option_type == "call":
        return float(S * _norm_cdf(d1) - K * math.exp(-r * T) * _norm_cdf(d2))
    return float(K * math.exp(-r * T) * _norm_cdf(-d2) - S * _norm_cdf(-d1))


def greeks(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: OptionType = "call",
) -> Dict[str, float]:
    """
    Option Greeks with brief interpretation hints.
    """
    _validate_bs_inputs(S, K, T, r, sigma)
    price = black_scholes(S, K, T, r, sigma, option_type)

    if T == 0 or sigma == 0:
        return {
            "price": price,
            "delta": 1.0 if option_type == "call" and S > K else 0.0,
            "gamma": 0.0,
            "theta": 0.0,
            "vega": 0.0,
            "rho": 0.0,
        }

    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    pdf_d1 = _norm_pdf(d1)

    delta = _norm_cdf(d1) if option_type == "call" else _norm_cdf(d1) - 1.0
    gamma = pdf_d1 / (S * sigma * math.sqrt(T))
    vega = S * pdf_d1 * math.sqrt(T) / 100.0  # per 1% vol move

    if option_type == "call":
        theta = (
            -S * pdf_d1 * sigma / (2 * math.sqrt(T))
            - r * K * math.exp(-r * T) * _norm_cdf(d2)
        ) / 365.0
        rho = K * T * math.exp(-r * T) * _norm_cdf(d2) / 100.0
    else:
        theta = (
            -S * pdf_d1 * sigma / (2 * math.sqrt(T))
            + r * K * math.exp(-r * T) * _norm_cdf(-d2)
        ) / 365.0
        rho = -K * T * math.exp(-r * T) * _norm_cdf(-d2) / 100.0

    return {
        "price": float(price),
        "delta": float(delta),
        "gamma": float(gamma),
        "theta": float(theta),
        "vega": float(vega),
        "rho": float(rho),
        "interpretation": {
            "delta": "Sensitivity to underlying price",
            "gamma": "Rate of change of delta",
            "theta": "Time decay per day",
            "vega": "Sensitivity to 1% vol change",
            "rho": "Sensitivity to 1% rate change",
        },
    }


def put_call_parity(
    call: float,
    put: float,
    S: float,
    K: float,
    r: float,
    T: float,
    *,
    tolerance: float = 0.01,
) -> Dict[str, Any]:
    """
    Verify put-call parity: C - P = S - K*exp(-rT).
    """
    lhs = call - put
    rhs = S - K * math.exp(-r * T)
    diff = lhs - rhs
    return {
        "lhs": float(lhs),
        "rhs": float(rhs),
        "difference": float(diff),
        "holds": abs(diff) <= tolerance,
        "tolerance": tolerance,
    }


def binomial(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    steps: int = 3,
    option_type: OptionType = "call",
    *,
    american: bool = False,
) -> Dict[str, Any]:
    """
    Cox-Ross-Rubinstein binomial tree pricing.
    """
    _validate_bs_inputs(S, K, T, r, sigma)
    if steps <= 0:
        raise ValidationError("steps must be positive")

    dt = T / steps
    u = math.exp(sigma * math.sqrt(dt))
    d = 1.0 / u
    p = (math.exp(r * dt) - d) / (u - d)
    if not 0 <= p <= 1:
        raise ValidationError("risk-neutral probability out of range; check inputs")

    # Build stock price tree
    stock_tree = np.zeros((steps + 1, steps + 1))
    for i in range(steps + 1):
        for j in range(i + 1):
            stock_tree[j, i] = S * (u ** (i - j)) * (d**j)

    # Option value tree (backward induction)
    option_tree = np.zeros_like(stock_tree)
    for j in range(steps + 1):
        s = stock_tree[j, steps]
        if option_type == "call":
            option_tree[j, steps] = max(s - K, 0.0)
        else:
            option_tree[j, steps] = max(K - s, 0.0)

    disc = math.exp(-r * dt)
    for i in range(steps - 1, -1, -1):
        for j in range(i + 1):
            hold = disc * (
                p * option_tree[j, i + 1] + (1 - p) * option_tree[j + 1, i + 1]
            )
            if american:
                s = stock_tree[j, i]
                intrinsic = (
                    max(s - K, 0.0) if option_type == "call" else max(K - s, 0.0)
                )
                option_tree[j, i] = max(hold, intrinsic)
            else:
                option_tree[j, i] = hold

    return {
        "price": float(option_tree[0, 0]),
        "stock_tree": stock_tree.tolist(),
        "option_tree": option_tree.tolist(),
        "u": u,
        "d": d,
        "p": p,
        "steps": steps,
    }


def payoff_diagram(
    strategy: str,
    legs: List[Dict[str, Any]],
    *,
    spot_range: Optional[Tuple[float, float]] = None,
    points: int = 100,
) -> Dict[str, List[float]]:
    """
    Payoff at expiry for a strategy (no plotting dependency).

    Each leg: {type: call|put|stock, position: long|short, strike, premium, quantity}
    """
    if not legs:
        raise ValidationError("legs must be a non-empty list")

    strikes = [leg.get("strike", 0) for leg in legs if leg.get("strike")]
    S_min = (
        spot_range[0]
        if spot_range
        else max(0.01, min(strikes) * 0.5 if strikes else 50)
    )
    S_max = spot_range[1] if spot_range else (max(strikes) * 1.5 if strikes else 200)
    spots = np.linspace(S_min, S_max, points).tolist()
    payoffs = []

    for s in spots:
        total = 0.0
        for leg in legs:
            qty = leg.get("quantity", 1)
            premium = leg.get("premium", 0.0)
            pos = leg.get("position", "long")
            sign = 1 if pos == "long" else -1
            ltype = leg.get("type", "call")
            strike = leg.get("strike", s)

            if ltype == "stock":
                total += sign * qty * (s - premium)
            elif ltype == "call":
                intrinsic = max(s - strike, 0.0)
                total += sign * qty * (intrinsic - premium)
            elif ltype == "put":
                intrinsic = max(strike - s, 0.0)
                total += sign * qty * (intrinsic - premium)
        payoffs.append(float(total))

    return {"spot_prices": spots, "payoffs": payoffs, "strategy": strategy}


def strategy_metrics(
    strategy: str,
    S: float,
    *,
    legs: Optional[List[Dict[str, Any]]] = None,
    K: Optional[float] = None,
    premium: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Max profit, max loss, and breakeven for common strategies.
    """
    strategy = strategy.lower().replace(" ", "_")

    if strategy == "covered_call":
        if K is None or premium is None:
            raise ValidationError("K and premium required for covered_call")
        return {
            "strategy": strategy,
            "max_profit": float(premium + (K - S)),
            "max_loss": float(S - premium),
            "breakeven": float(S - premium),
        }
    if strategy == "protective_put":
        if K is None or premium is None:
            raise ValidationError("K and premium required for protective_put")
        return {
            "strategy": strategy,
            "max_profit": None,
            "max_loss": float(S - K + premium),
            "breakeven": float(S + premium),
        }
    if strategy == "bull_call_spread":
        if legs and len(legs) >= 2:
            long_k = legs[0]["strike"]
            short_k = legs[1]["strike"]
            net_premium = legs[0].get("premium", 0) - legs[1].get("premium", 0)
        else:
            raise ValidationError("bull_call_spread requires two legs with strikes")
        width = short_k - long_k
        return {
            "strategy": strategy,
            "max_profit": float(width - net_premium),
            "max_loss": float(net_premium),
            "breakeven": float(long_k + net_premium),
        }
    if strategy == "straddle":
        if K is None or premium is None:
            raise ValidationError("K and premium required for straddle")
        return {
            "strategy": strategy,
            "max_profit": None,
            "max_loss": float(premium),
            "breakeven_low": float(K - premium),
            "breakeven_high": float(K + premium),
        }

    if legs:
        diagram = payoff_diagram(strategy, legs)
        payoffs = diagram["payoffs"]
        spots = diagram["spot_prices"]
        max_profit = max(payoffs)
        max_loss = min(payoffs)
        breakevens = []
        for i in range(1, len(payoffs)):
            if payoffs[i - 1] * payoffs[i] <= 0 and payoffs[i] != payoffs[i - 1]:
                # linear interpolate zero crossing
                x0, x1 = spots[i - 1], spots[i]
                y0, y1 = payoffs[i - 1], payoffs[i]
                be = x0 - y0 * (x1 - x0) / (y1 - y0)
                breakevens.append(round(be, 4))
        return {
            "strategy": strategy,
            "max_profit": float(max_profit) if max_profit > 0 else None,
            "max_loss": float(max_loss),
            "breakevens": breakevens,
        }

    raise ValidationError(f"Unknown strategy: {strategy}")
