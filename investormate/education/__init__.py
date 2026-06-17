"""Educational layer: explain, show_work, CFA tags, and practice problems."""

from .knowledge import RATIO_KNOWLEDGE, get_ratio_knowledge, interpret_ratio_value
from .practice import generate

__all__ = [
    "RATIO_KNOWLEDGE",
    "get_ratio_knowledge",
    "interpret_ratio_value",
    "generate",
]
