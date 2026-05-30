"""Tests for the centralized logging helper."""

import logging

from investormate.utils.logging import get_logger, ROOT_LOGGER_NAME


def test_root_logger_has_null_handler():
    root = logging.getLogger(ROOT_LOGGER_NAME)
    assert any(isinstance(h, logging.NullHandler) for h in root.handlers)


def test_get_logger_namespaces_under_package():
    logger = get_logger("investormate.core.investor")
    assert logger.name == "investormate.core.investor"


def test_get_logger_nests_bare_name():
    logger = get_logger("mymodule")
    assert logger.name == "investormate.mymodule"


def test_get_logger_none_returns_root():
    assert get_logger(None).name == ROOT_LOGGER_NAME


def test_library_is_silent_by_default(caplog):
    # With only the NullHandler and default level, nothing propagates to caller
    logger = get_logger("test")
    with caplog.at_level(logging.CRITICAL, logger=ROOT_LOGGER_NAME):
        logger.info("this should not appear at CRITICAL level")
    assert "this should not appear" not in caplog.text
