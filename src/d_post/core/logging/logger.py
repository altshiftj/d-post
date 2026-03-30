"""Logging helpers that emit structured JSON to disk and stdout."""

from __future__ import annotations

import json
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from threading import Lock

BASE_DIR = Path("C:/Watchdog")
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "watchdog.log"

APP_LOGGER_NAME = "d_post"
LEGACY_LOGGER_NAME = "watchdog"
_HANDLER_MARKER = "_d_post_managed"
_LOGGER_CONFIG_LOCK = Lock()


class JSONFormatter(logging.Formatter):
    """Formatter that serializes log records into a JSON payload for ingestion."""

    def format(self, record: logging.LogRecord) -> str:
        """Render a log record as a JSON string."""
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "filename": record.filename,
            "line": record.lineno,
        }
        session_id = getattr(record, "session_id", None)
        if session_id is not None:
            log_record["session_id"] = session_id
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


def setup_logger(name: str = LEGACY_LOGGER_NAME) -> logging.Logger:
    """Return an application logger backed by one shared handler set."""
    namespace_logger = _configure_namespace_logger()
    resolved_name = _normalize_logger_name(name)
    logger = logging.getLogger(resolved_name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = True

    if logger is not namespace_logger:
        _remove_managed_handlers(logger)

    return logger


def _configure_namespace_logger() -> logging.Logger:
    """Ensure the top-level application logger owns the shared handlers."""
    with _LOGGER_CONFIG_LOCK:
        logger = logging.getLogger(APP_LOGGER_NAME)
        logger.setLevel(logging.DEBUG)
        logger.propagate = True

        if _has_managed_handlers(logger):
            return logger

        formatter = JSONFormatter()
        for handler in _build_managed_handlers(formatter):
            logger.addHandler(handler)

        return logger


def _normalize_logger_name(name: str) -> str:
    """Map legacy or bare logger names into the application namespace."""
    cleaned = name.strip() or APP_LOGGER_NAME
    if cleaned == LEGACY_LOGGER_NAME:
        return APP_LOGGER_NAME
    if cleaned.startswith(f"{LEGACY_LOGGER_NAME}."):
        return cleaned.replace(LEGACY_LOGGER_NAME, APP_LOGGER_NAME, 1)
    if cleaned == APP_LOGGER_NAME or cleaned.startswith(f"{APP_LOGGER_NAME}."):
        return cleaned
    return f"{APP_LOGGER_NAME}.{cleaned}"


def _has_managed_handlers(logger: logging.Logger) -> bool:
    """Return whether the logger already owns Watchdog-managed handlers."""
    return any(getattr(handler, _HANDLER_MARKER, False) for handler in logger.handlers)


def _remove_managed_handlers(logger: logging.Logger) -> None:
    """Remove any handlers previously installed by :func:`setup_logger`."""
    for handler in list(logger.handlers):
        if not getattr(handler, _HANDLER_MARKER, False):
            continue
        logger.removeHandler(handler)
        handler.close()


def _build_managed_handlers(
    formatter: logging.Formatter,
) -> tuple[logging.Handler, ...]:
    """Create the shared handler set for the application namespace."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(str(LOG_FILE), maxBytes=5_000_000, backupCount=3)
    _mark_managed_handler(file_handler)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    handlers: list[logging.Handler] = [file_handler]
    if sys.stdout:
        try:
            console_handler = logging.StreamHandler(stream=sys.stdout)
        except Exception:  # pragma: no cover - defensive console fallback
            return tuple(handlers)
        _mark_managed_handler(console_handler)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        handlers.append(console_handler)

    return tuple(handlers)


def _mark_managed_handler(handler: logging.Handler) -> None:
    """Tag a handler so repeated setup calls can identify shared handlers."""
    setattr(handler, _HANDLER_MARKER, True)
