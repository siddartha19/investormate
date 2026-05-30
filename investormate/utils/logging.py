"""
Centralized logging for InvestorMate.

Libraries should not configure logging handlers or print to stdout. Instead we
expose a package logger with a :class:`~logging.NullHandler` attached so that
diagnostic messages are silent by default and fully controllable by the
consuming application.

Usage::

    from ..utils.logging import get_logger

    logger = get_logger(__name__)
    logger.warning("Failed to fetch data for %s", ticker)

Consumers can opt in to output with::

    import logging
    logging.getLogger("investormate").setLevel(logging.INFO)
    logging.basicConfig()
"""

from __future__ import annotations

import logging

ROOT_LOGGER_NAME = "investormate"

# Attach a NullHandler once so "No handlers could be found" warnings never fire
# and the library stays silent unless the application configures logging.
_root_logger = logging.getLogger(ROOT_LOGGER_NAME)
if not any(isinstance(h, logging.NullHandler) for h in _root_logger.handlers):
    _root_logger.addHandler(logging.NullHandler())


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Return a logger namespaced under ``investormate``.

    Args:
        name: Typically ``__name__`` of the calling module. If it already lives
            under the ``investormate`` package the module logger is returned
            as-is; otherwise it is nested beneath the package root.

    Returns:
        A :class:`logging.Logger` instance.
    """
    if not name or name == ROOT_LOGGER_NAME:
        return _root_logger
    if name.startswith(ROOT_LOGGER_NAME + "."):
        return logging.getLogger(name)
    return logging.getLogger(f"{ROOT_LOGGER_NAME}.{name}")
