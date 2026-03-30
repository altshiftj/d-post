from __future__ import annotations

from collections.abc import Iterator
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

import pytest

import d_post.core.logging.logger as logger_mod

TEST_LOGGER_ALPHA = "d_post.tests.logging.alpha"
TEST_LOGGER_BETA = "d_post.tests.logging.beta"
TEST_LOGGER_CHILD = "d_post.tests.logging.child"
TEST_LOGGER_WRITER = "d_post.tests.logging.writer"


def _remove_and_close_handlers(logger: logging.Logger) -> None:
    """Detach and close every handler currently attached to a logger."""
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()


@pytest.fixture
def isolated_watchdog_logging(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[Path]:
    """Redirect Watchdog logging to a temporary file and isolate namespace handlers."""
    namespace_logger = logging.getLogger("d_post")
    original_handlers = list(namespace_logger.handlers)
    original_level = namespace_logger.level
    original_propagate = namespace_logger.propagate

    for handler in original_handlers:
        namespace_logger.removeHandler(handler)

    _remove_and_close_handlers(logging.getLogger(TEST_LOGGER_ALPHA))
    _remove_and_close_handlers(logging.getLogger(TEST_LOGGER_BETA))
    _remove_and_close_handlers(logging.getLogger(TEST_LOGGER_CHILD))
    _remove_and_close_handlers(logging.getLogger(TEST_LOGGER_WRITER))

    log_path = tmp_path / "watchdog.log"
    monkeypatch.setattr(logger_mod, "LOG_DIR", tmp_path)
    monkeypatch.setattr(logger_mod, "LOG_FILE", log_path)

    yield log_path

    _remove_and_close_handlers(logging.getLogger(TEST_LOGGER_ALPHA))
    _remove_and_close_handlers(logging.getLogger(TEST_LOGGER_BETA))
    _remove_and_close_handlers(logging.getLogger(TEST_LOGGER_CHILD))
    _remove_and_close_handlers(logging.getLogger(TEST_LOGGER_WRITER))

    for handler in list(namespace_logger.handlers):
        namespace_logger.removeHandler(handler)
        if handler not in original_handlers:
            handler.close()

    namespace_logger.setLevel(original_level)
    namespace_logger.propagate = original_propagate
    for handler in original_handlers:
        namespace_logger.addHandler(handler)


def test_setup_logger_reuses_one_file_handler_for_namespace(
    isolated_watchdog_logging: Path,
) -> None:
    """Multiple module loggers should share one file handler for the app namespace."""
    logger_mod.setup_logger(TEST_LOGGER_ALPHA)
    logger_mod.setup_logger(TEST_LOGGER_BETA)

    namespace_logger = logging.getLogger("d_post")
    alpha_logger = logging.getLogger(TEST_LOGGER_ALPHA)
    beta_logger = logging.getLogger(TEST_LOGGER_BETA)

    file_handlers = [
        *[
            handler
            for handler in namespace_logger.handlers
            if isinstance(handler, RotatingFileHandler)
        ],
        *[
            handler
            for handler in alpha_logger.handlers
            if isinstance(handler, RotatingFileHandler)
        ],
        *[
            handler
            for handler in beta_logger.handlers
            if isinstance(handler, RotatingFileHandler)
        ],
    ]

    assert isolated_watchdog_logging.parent.exists()
    assert len(file_handlers) == 1
    assert file_handlers[0] in namespace_logger.handlers


def test_setup_logger_returns_child_loggers_without_direct_file_handlers(
    isolated_watchdog_logging: Path,
) -> None:
    """Child module loggers should rely on propagation instead of owning file handlers."""
    child_logger = logger_mod.setup_logger(TEST_LOGGER_CHILD)

    assert isolated_watchdog_logging.parent.exists()
    assert not any(
        isinstance(handler, RotatingFileHandler) for handler in child_logger.handlers
    )
    assert child_logger.propagate is True


def test_child_logger_writes_via_namespace_handler(
    isolated_watchdog_logging: Path,
) -> None:
    """Child logger output should flow through the shared namespace file handler."""
    child_logger = logger_mod.setup_logger(TEST_LOGGER_WRITER)
    namespace_logger = logging.getLogger("d_post")

    assert any(
        isinstance(handler, RotatingFileHandler)
        for handler in namespace_logger.handlers
    )

    child_logger.info("propagated test message")

    for handler in namespace_logger.handlers:
        handler.flush()

    contents = isolated_watchdog_logging.read_text(encoding="utf-8")
    assert '"message": "propagated test message"' in contents
    assert f'"logger": "{TEST_LOGGER_WRITER}"' in contents
