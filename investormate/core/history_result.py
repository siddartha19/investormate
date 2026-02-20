"""
Result type for Stock.history(source_trace=True).
Exposes .data (DataFrame) and .trace (dict) for data provenance.
"""

from dataclasses import dataclass
from typing import Any, Dict

import pandas as pd


@dataclass
class HistoryResult:
    """
    Returned by Stock.history(..., source_trace=True).
    Holds the OHLCV DataFrame and a trace dict for data provenance.
    """

    data: pd.DataFrame
    trace: Dict[str, Any]

    def __repr__(self) -> str:
        return f"HistoryResult(data=DataFrame(shape={self.data.shape}), trace={list(self.trace.keys())})"
