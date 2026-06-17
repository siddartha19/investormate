"""
Ratio knowledge registry for the educational layer.

Deterministic explain/show_work — no AI key required.
"""

from typing import Any, Dict, List, Optional


RATIO_KNOWLEDGE: Dict[str, Dict[str, Any]] = {
    "pe": {
        "name": "Price-to-Earnings (P/E)",
        "formula": "P/E = Price per Share / Earnings per Share",
        "variables": {
            "price": "Current market price per share",
            "eps": "Earnings per share (typically trailing twelve months)",
        },
        "interpretation": "Higher P/E may indicate growth expectations; lower P/E may suggest value or distress.",
        "cfa_topic": "Equity Investments (L1)",
        "healthy_range": (5, 35),
    },
    "pb": {
        "name": "Price-to-Book (P/B)",
        "formula": "P/B = Market Price / Book Value per Share",
        "variables": {
            "price": "Market price",
            "book_value": "Shareholders' equity per share",
        },
        "interpretation": "Compares market value to accounting net asset value.",
        "cfa_topic": "Equity Investments (L1)",
        "healthy_range": (0.5, 5),
    },
    "current_ratio": {
        "name": "Current Ratio",
        "formula": "Current Ratio = Current Assets / Current Liabilities",
        "variables": {
            "current_assets": "Assets due within one year",
            "current_liabilities": "Obligations due within one year",
        },
        "interpretation": "Measures short-term liquidity. Below 1.0 may signal liquidity stress.",
        "cfa_topic": "Financial Statement Analysis (L1)",
        "healthy_range": (1.0, 3.0),
    },
    "roe": {
        "name": "Return on Equity (ROE)",
        "formula": "ROE = Net Income / Shareholders' Equity",
        "variables": {
            "net_income": "Bottom-line profit",
            "equity": "Shareholders' equity",
        },
        "interpretation": "Profitability relative to equity capital. DuPont breaks ROE into margin × turnover × leverage.",
        "cfa_topic": "Financial Statement Analysis (L1)",
        "healthy_range": (0.08, 0.30),
    },
    "roic": {
        "name": "Return on Invested Capital (ROIC)",
        "formula": "ROIC = NOPAT / Invested Capital",
        "variables": {
            "nopat": "Net operating profit after tax",
            "invested_capital": "Total assets minus non-interest-bearing current liabilities",
        },
        "interpretation": "Efficiency of capital deployment. Compare to WACC for value creation.",
        "cfa_topic": "Corporate Issuers (L1)",
        "healthy_range": (0.08, 0.25),
    },
    "wacc": {
        "name": "Weighted Average Cost of Capital (WACC)",
        "formula": "WACC = (E/V)×Re + (D/V)×Rd×(1−Tc)",
        "variables": {
            "E": "Market value of equity",
            "D": "Market value of debt",
            "Re": "Cost of equity",
            "Rd": "Cost of debt",
            "Tc": "Tax rate",
        },
        "interpretation": "Minimum return a company must earn on assets to satisfy capital providers.",
        "cfa_topic": "Corporate Issuers (L1)",
        "healthy_range": (0.06, 0.15),
    },
    "debt_to_equity": {
        "name": "Debt-to-Equity",
        "formula": "D/E = Total Debt / Total Equity",
        "variables": {"debt": "Total debt", "equity": "Shareholders' equity"},
        "interpretation": "Financial leverage. Industry norms vary widely.",
        "cfa_topic": "Financial Statement Analysis (L1)",
        "healthy_range": (0, 2.0),
    },
    "profit_margin": {
        "name": "Net Profit Margin",
        "formula": "Net Margin = Net Income / Revenue",
        "variables": {"net_income": "Net income", "revenue": "Total revenue"},
        "interpretation": "Percentage of revenue retained as profit.",
        "cfa_topic": "Financial Statement Analysis (L1)",
        "healthy_range": (0.05, 0.25),
    },
    "quick_ratio": {
        "name": "Quick Ratio",
        "formula": "Quick Ratio = (Current Assets − Inventory) / Current Liabilities",
        "variables": {
            "current_assets": "Current assets",
            "inventory": "Inventory",
            "current_liabilities": "Current liabilities",
        },
        "interpretation": "Stricter liquidity test excluding inventory.",
        "cfa_topic": "Financial Statement Analysis (L1)",
        "healthy_range": (0.8, 2.5),
    },
}


def get_ratio_knowledge(name: str) -> Optional[Dict[str, Any]]:
    """Look up knowledge entry by ratio key (case-insensitive)."""
    return RATIO_KNOWLEDGE.get(name.lower().replace(" ", "_"))


def interpret_ratio_value(name: str, value: Optional[float]) -> str:
    """Plain-English assessment for a single ratio value."""
    if value is None:
        return "Value unavailable — insufficient data."

    entry = get_ratio_knowledge(name)
    if not entry:
        return f"Value is {value:.4f}."

    healthy = entry.get("healthy_range")
    if healthy:
        lo, hi = healthy
        if value < lo:
            return f"Below typical range ({lo}–{hi}): may indicate weakness or value depending on context."
        if value > hi:
            return f"Above typical range ({lo}–{hi}): may indicate strength or overvaluation depending on context."
        return f"Within typical range ({lo}–{hi}): appears reasonable on a standalone basis."

    return entry.get("interpretation", f"Value is {value:.4f}.")
