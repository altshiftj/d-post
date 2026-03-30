"""Bootstrap helpers used by the Watchdog entrypoint."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Literal, Sequence

from dotenv import load_dotenv
from prometheus_client import start_http_server

from d_post.core.app.device_watchdog_app import DeviceWatchdogApp
from d_post.core.config import ConfigService, DeviceConfig, init_config
from d_post.core.logging.logger import setup_logger
from d_post.core.storage.filesystem_utils import init_dirs
from d_post.core.sync.sync_abstract import ISyncManager
from d_post.core.sync.sync_noop import NoopSyncManager
from d_post.core.ui.adapters import UiInteractionAdapter, UiTaskScheduler
from d_post.core.ui.ui_tkinter import TKinterUI
from d_post.loader import get_devices_for_pc, load_device_plugin, load_pc_plugin

try:
    from d_post.observability import start_observability_server
except ModuleNotFoundError as _obs_exc:
    start_observability_server = None
    _OBSERVABILITY_IMPORT_ERROR = _obs_exc
else:
    _OBSERVABILITY_IMPORT_ERROR = None

logger = setup_logger(__name__)

DEFAULT_PROMETHEUS_PORT = 8000
DEFAULT_OBSERVABILITY_PORT = 8001
DEFAULT_SYNC_BACKEND = "noop"
SyncBackend = Literal["noop", "kadi"]


class StartupError(RuntimeError):
    """Raised when bootstrap configuration fails."""


class MissingConfiguration(StartupError):
    """Raised when required environment configuration is missing."""


@dataclass(frozen=True)
class StartupSettings:
    """Resolved startup settings for the Watchdog application."""

    pc_name: str
    device_names: tuple[str, ...]
    prometheus_port: int = DEFAULT_PROMETHEUS_PORT
    observability_port: int = DEFAULT_OBSERVABILITY_PORT
    sync_backend: SyncBackend = DEFAULT_SYNC_BACKEND
    env_source: Path | None = None


@dataclass
class BootstrapContext:
    """Concrete artefacts returned by :func:`bootstrap` for the entrypoint."""

    settings: StartupSettings
    config_service: ConfigService
    app: DeviceWatchdogApp
    ui: TKinterUI
    sync_manager: ISyncManager
    interactions: UiInteractionAdapter
    scheduler: UiTaskScheduler


def bootstrap(
    settings: StartupSettings | None = None,
    *,
    ui_factory: Callable[[], TKinterUI] = TKinterUI,
    sync_manager_factory: Callable[[UiInteractionAdapter], ISyncManager] | None = None,
) -> BootstrapContext:
    """Initialise configuration, supporting services, and the UI stack."""

    resolved = settings or collect_startup_settings()
    logger.info(
        "Starting Watchdog with PC=%s, devices=%s, sync backend=%s",
        resolved.pc_name,
        ", ".join(resolved.device_names),
        resolved.sync_backend,
    )

    if sync_manager_factory is None:
        sync_manager_factory = _resolve_sync_manager_factory(resolved.sync_backend)

    config_service = _build_config_service(resolved.pc_name, resolved.device_names)
    init_dirs()

    start_http_server(resolved.prometheus_port)
    logger.info(
        "Prometheus metrics server listening on port %d", resolved.prometheus_port
    )

    if start_observability_server is not None:
        start_observability_server(port=resolved.observability_port)
        logger.info(
            "Observability server listening on port %d", resolved.observability_port
        )
    elif _OBSERVABILITY_IMPORT_ERROR is not None:
        logger.warning("Observability server disabled: %s", _OBSERVABILITY_IMPORT_ERROR)

    ui = ui_factory()
    interaction_adapter = UiInteractionAdapter(ui)
    scheduler = UiTaskScheduler(ui)
    sync_manager = sync_manager_factory(interaction_adapter)

    app = DeviceWatchdogApp(
        ui=ui,
        sync_manager=sync_manager,
        config_service=config_service,
        interactions=interaction_adapter,
        scheduler=scheduler,
    )

    return BootstrapContext(
        settings=resolved,
        config_service=config_service,
        app=app,
        ui=ui,
        sync_manager=sync_manager,
        interactions=interaction_adapter,
        scheduler=scheduler,
    )


def collect_startup_settings(
    *,
    pc_name: str | None = None,
    device_names: Sequence[str] | None = None,
    load_env: bool = True,
) -> StartupSettings:
    """Resolve startup settings from env vars and plugin metadata."""

    env_source = load_bundled_env() if load_env else None

    resolved_pc = (pc_name or os.getenv("PC_NAME", "")).strip()
    if not resolved_pc:
        raise MissingConfiguration(
            "PC_NAME must be provided via environment or arguments."
        )

    resolved_devices = tuple(
        device_names or _list_from_env(os.getenv("DEVICE_PLUGINS", ""))
    )
    if not resolved_devices:
        resolved_devices = tuple(get_devices_for_pc(resolved_pc))
        if not resolved_devices:
            raise MissingConfiguration(
                "No device plugins were resolved. Set DEVICE_PLUGINS or configure the PC plugin."
            )

    prometheus_port = _coerce_port(
        os.getenv("PROMETHEUS_PORT"), DEFAULT_PROMETHEUS_PORT, "PROMETHEUS_PORT"
    )
    observability_port = _coerce_port(
        os.getenv("OBSERVABILITY_PORT"),
        DEFAULT_OBSERVABILITY_PORT,
        "OBSERVABILITY_PORT",
    )
    sync_backend = _coerce_sync_backend(os.getenv("SYNC_BACKEND"))

    return StartupSettings(
        pc_name=resolved_pc,
        device_names=resolved_devices,
        prometheus_port=prometheus_port,
        observability_port=observability_port,
        sync_backend=sync_backend,
        env_source=env_source,
    )


def load_bundled_env(bundle_dir: Path | None = None) -> Path | None:
    """Load the .env shipped with the frozen bundle (if present)."""

    env_dir = bundle_dir or _resolve_bundle_dir()
    env_path = env_dir / ".env"
    if not env_path.exists():
        logger.debug("No bundled .env file found at %s", env_path)
        return None

    load_dotenv(env_path, override=False)
    logger.info("Loaded environment from %s", env_path)
    return env_path


def _resolve_bundle_dir() -> Path:
    # When running from a PyInstaller bundle, sys._MEIPASS holds the temp dir.
    if bool(getattr(sys, "frozen", False)):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)

    module_path = Path(__file__).resolve()
    try:
        return module_path.parents[4] / "build"
    except IndexError:
        return module_path.parent


def _build_config_service(pc_name: str, device_names: Iterable[str]) -> ConfigService:
    pc_plugin = load_pc_plugin(pc_name)
    pc_config = pc_plugin.get_config()

    device_configs: list[DeviceConfig] = []
    for device_name in device_names:
        plugin = load_device_plugin(device_name)
        device_configs.append(plugin.get_config())

    return init_config(pc_config, device_configs)


def _resolve_sync_manager_factory(
    sync_backend: SyncBackend,
) -> Callable[[UiInteractionAdapter], ISyncManager]:
    """Return the sync manager factory for the selected backend."""
    if sync_backend == "noop":
        return NoopSyncManager

    if sync_backend == "kadi":
        try:
            from d_post.core.sync.sync_kadi import KadiSyncManager
        except ModuleNotFoundError as exc:
            raise StartupError(
                "SYNC_BACKEND='kadi' requires the optional dependency set. Install d-post[kadi] before selecting it."
            ) from exc
        return KadiSyncManager

    raise StartupError(f"Unsupported sync backend: {sync_backend!r}")


def _list_from_env(raw: str) -> list[str]:
    tokens = [
        token.strip() for token in raw.replace(";", ",").split(",") if token.strip()
    ]
    return tokens


def _coerce_sync_backend(raw: str | None) -> SyncBackend:
    """Normalize and validate the requested sync backend."""
    if raw is None or raw.strip() == "":
        return DEFAULT_SYNC_BACKEND

    normalized = raw.strip().lower()
    if normalized not in {"noop", "kadi"}:
        raise StartupError(
            f"Invalid value for SYNC_BACKEND: {raw!r}. Expected one of: noop, kadi."
        )
    return normalized


def _coerce_port(raw: str | None, default: int, name: str) -> int:
    if raw is None or raw.strip() == "":
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise StartupError(f"Invalid integer value for {name}: {raw!r}") from exc
    if value <= 0:
        raise StartupError(f"{name} must be a positive integer. Got {value}.")
    return value
