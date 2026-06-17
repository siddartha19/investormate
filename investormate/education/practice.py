"""
Practice problem generator for finance students.
"""

import random
from typing import Any, Dict, List, Literal, Optional

from ..finance import bonds, options, tvm
from ..utils.exceptions import ValidationError

Difficulty = Literal["easy", "medium", "hard"]
Topic = Literal["tvm", "bonds", "options"]


def _difficulty_params(difficulty: Difficulty) -> Dict[str, Any]:
    if difficulty == "easy":
        return {
            "rate_range": (0.04, 0.08),
            "n_range": (3, 10),
            "amount_range": (500, 5000),
        }
    if difficulty == "hard":
        return {
            "rate_range": (0.06, 0.15),
            "n_range": (10, 30),
            "amount_range": (5000, 50000),
        }
    return {
        "rate_range": (0.05, 0.12),
        "n_range": (5, 20),
        "amount_range": (1000, 20000),
    }


def generate(
    topic: Topic,
    difficulty: Difficulty = "medium",
    *,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Generate a random practice problem with worked solution.

    Args:
        topic: ``tvm``, ``bonds``, or ``options``
        difficulty: ``easy``, ``medium``, or ``hard``
        seed: Optional RNG seed for reproducible problems
    """
    if seed is not None:
        random.seed(seed)

    topic = topic.lower()  # type: ignore[assignment]
    if topic == "tvm":
        return _generate_tvm(difficulty)
    if topic == "bonds":
        return _generate_bonds(difficulty)
    if topic == "options":
        return _generate_options(difficulty)
    raise ValidationError(f"Unknown topic: {topic}. Use tvm, bonds, or options.")


def _generate_tvm(difficulty: Difficulty) -> Dict[str, Any]:
    params = _difficulty_params(difficulty)
    kind = random.choice(["pv", "fv", "annuity_pv", "npv", "irr"])

    if kind == "pv":
        fv = random.randint(*params["amount_range"])
        rate = round(random.uniform(*params["rate_range"]), 3)
        n = random.randint(*params["n_range"])
        answer = tvm.present_value(fv, rate, n)
        return {
            "topic": "tvm",
            "difficulty": difficulty,
            "question": f"What is the present value of ${fv:,.0f} received in {n} years at {rate*100:.1f}%?",
            "parameters": {"fv": fv, "rate": rate, "n": n},
            "answer": round(answer, 2),
            "solution_steps": [
                f"PV = FV / (1+r)^n = {fv} / (1+{rate})^{n}",
                f"PV = ${answer:,.2f}",
            ],
        }

    if kind == "fv":
        pv = random.randint(*params["amount_range"])
        rate = round(random.uniform(*params["rate_range"]), 3)
        n = random.randint(*params["n_range"])
        answer = tvm.future_value(pv, rate, n)
        return {
            "topic": "tvm",
            "difficulty": difficulty,
            "question": f"What is the future value of ${pv:,.0f} invested for {n} years at {rate*100:.1f}%?",
            "parameters": {"pv": pv, "rate": rate, "n": n},
            "answer": round(answer, 2),
            "solution_steps": [
                f"FV = PV × (1+r)^n = {pv} × (1+{rate})^{n}",
                f"FV = ${answer:,.2f}",
            ],
        }

    if kind == "annuity_pv":
        pmt = random.randint(100, 1000)
        rate = round(random.uniform(*params["rate_range"]), 3)
        n = random.randint(5, 20)
        answer = tvm.annuity_pv(pmt, rate, n)
        return {
            "topic": "tvm",
            "difficulty": difficulty,
            "question": f"What is the PV of a ${pmt}/year ordinary annuity for {n} years at {rate*100:.1f}%?",
            "parameters": {"pmt": pmt, "rate": rate, "n": n},
            "answer": round(answer, 2),
            "solution_steps": [
                f"PV = PMT × [1 - (1+r)^-n] / r",
                f"PV = ${answer:,.2f}",
            ],
        }

    if kind == "npv":
        cfs = [-random.randint(2000, 10000)] + [
            random.randint(500, 3000) for _ in range(3)
        ]
        rate = round(random.uniform(0.08, 0.15), 3)
        answer = tvm.npv(rate, cfs)
        return {
            "topic": "tvm",
            "difficulty": difficulty,
            "question": f"Compute NPV at {rate*100:.1f}% for cash flows: {cfs}",
            "parameters": {"cashflows": cfs, "rate": rate},
            "answer": round(answer, 2),
            "solution_steps": [
                "Discount each cash flow and sum",
                f"NPV = ${answer:,.2f}",
            ],
        }

    # irr
    cfs = [-1000, 400, 400, 400]
    answer = tvm.irr(cfs)
    return {
        "topic": "tvm",
        "difficulty": difficulty,
        "question": f"Find the IRR for cash flows: {cfs}",
        "parameters": {"cashflows": cfs},
        "answer": round(answer, 4),
        "solution_steps": [
            "Solve for rate where NPV = 0",
            f"IRR = {answer*100:.2f}%",
        ],
    }


def _generate_bonds(difficulty: Difficulty) -> Dict[str, Any]:
    face = 1000
    coupon = round(random.choice([0.04, 0.05, 0.06, 0.07, 0.08]), 3)
    ytm = round(coupon + random.uniform(-0.02, 0.02), 3)
    n = random.choice([5, 10, 15, 20])
    b = bonds.Bond(face=face, coupon=coupon, ytm=ytm, n=n)
    price = b.price()
    duration = b.modified_duration()
    return {
        "topic": "bonds",
        "difficulty": difficulty,
        "question": (
            f"A {n}-year bond pays {coupon*100:.1f}% annual coupon (semiannual), "
            f"YTM = {ytm*100:.1f}%. What is the clean price?"
        ),
        "parameters": {"face": face, "coupon": coupon, "ytm": ytm, "n": n},
        "answer": round(price, 2),
        "solution_steps": [
            "Discount semiannual coupons and face value at periodic YTM",
            f"Clean price = ${price:,.2f}",
            f"Modified duration ≈ {duration:.2f} years",
        ],
        "bonus": {"modified_duration": round(duration, 4)},
    }


def _generate_options(difficulty: Difficulty) -> Dict[str, Any]:
    S = random.randint(80, 150)
    K = S + random.choice([-10, -5, 0, 5, 10])
    T = random.choice([0.25, 0.5, 1.0])
    r = 0.05
    sigma = round(random.uniform(0.15, 0.35), 2)
    opt_type = random.choice(["call", "put"])
    price = options.black_scholes(S, K, T, r, sigma, opt_type)
    g = options.greeks(S, K, T, r, sigma, opt_type)
    return {
        "topic": "options",
        "difficulty": difficulty,
        "question": (
            f"Black-Scholes price for a European {opt_type}: S={S}, K={K}, "
            f"T={T}yr, r=5%, σ={sigma*100:.0f}%"
        ),
        "parameters": {
            "S": S,
            "K": K,
            "T": T,
            "r": r,
            "sigma": sigma,
            "type": opt_type,
        },
        "answer": round(price, 2),
        "solution_steps": [
            "Apply Black-Scholes formula with d1, d2",
            f"Price = ${price:.2f}",
            f"Delta = {g['delta']:.4f}",
        ],
        "bonus": {"greeks": {k: g[k] for k in ("delta", "gamma", "theta", "vega")}},
    }
