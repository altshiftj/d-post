# Source Package Map

This package contains the `d-post` runtime, plugin loading code, observability
endpoints, reference plugins, and the local processing pipeline.

## Main Areas

| Path | Purpose |
| --- | --- |
| [core/](core/) | Runtime app, configuration, processing, records, storage, sync, logging, and UI adapters. |
| [device_plugins/](device_plugins/README.md) | Device plugin base class and synthetic reference device plugin. |
| [pc_plugins/](pc_plugins/README.md) | PC plugin base class and synthetic reference PC profile. |
| [loader.py](loader.py) | Helpers that load registered PC and device plugins. |
| [plugin_system.py](plugin_system.py) | Pluggy hook registration and plugin manager setup. |
| [metrics.py](metrics.py) | Prometheus metric registration and server startup helpers. |
| [observability.py](observability.py) | Optional health and log endpoints. |

## Core Runtime Map

| Path | Purpose |
| --- | --- |
| [core/app/](core/app/) | Startup bootstrap and the Tkinter-backed watchdog application. |
| [core/config/](core/config/) | Dataclasses and service layer for PC and device configuration. |
| [core/interactions/](core/interactions/) | UI-facing interaction messages and ports. |
| [core/processing/](core/processing/) | Device resolution, stability checks, routing, rename flow, and file processing orchestration. |
| [core/records/](core/records/) | Local record model and persistence manager. |
| [core/session/](core/session/) | Session lifecycle and inactivity handling. |
| [core/storage/](core/storage/) | Filesystem helpers for record paths, moves, and setup. |
| [core/sync/](core/sync/) | Sync interface, offline-safe noop backend, and optional Kadi backend. |
| [core/ui/](core/ui/) | Tkinter UI implementation and UI adapter helpers. |

## Related Docs

- [Root README](../../README.md)
- [Documentation map](../../docs/README.md)
- [PC plugin guide](pc_plugins/README.md)
- [Device plugin guide](device_plugins/README.md)
