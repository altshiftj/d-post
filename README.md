# d-post

`d-post` is a Windows-first desktop app for a repetitive lab-data problem:
files arrive from instruments, they need to be recognized, renamed, and moved
into a useful record structure, and doing that by hand is slow and error-prone.

This repository contains the public runtime behind that workflow. It includes
the plugin system, Tkinter UI, local record tracking, optional sync backends,
and two synthetic reference plugins, `test_pc` and `test_device`.

## Which Doc Should I Read?

| Audience | Start here | Use it for |
| --- | --- | --- |
| New users | This README | Installing the package, selecting the reference plugins, and starting the app. |
| Contributors | [CONTRIBUTING.md](CONTRIBUTING.md) | Development setup, checks, and contribution expectations. |
| Runtime readers | [docs/README.md](docs/README.md) | Maintained documentation map and current reference pages. |
| Source readers | [src/d_post/README.md](src/d_post/README.md) | Package layout and the main runtime areas. |
| PC plugin authors | [src/d_post/pc_plugins/README.md](src/d_post/pc_plugins/README.md) | Workstation-level configuration plugins. |
| Device plugin authors | [src/d_post/device_plugins/README.md](src/d_post/device_plugins/README.md) | Device-level selectors, metadata, and processors. |
| Security reporters | [SECURITY.md](SECURITY.md) | Vulnerability reporting guidance. |

## Quick Start

Install the package:

```powershell
python -m pip install .
```

Set the synthetic reference environment:

```powershell
$env:PC_NAME = "test_pc"
$env:DEVICE_PLUGINS = "test_device"
$env:SYNC_BACKEND = "noop"
```

Start the app:

```powershell
python -m d_post
```

After install, the console entrypoint also works:

```powershell
d-post
```

If you leave `DEVICE_PLUGINS` unset, `d-post` will try to infer the device side
from the selected PC plugin.

## What The App Does

At a high level, `d-post`:

1. loads a PC plugin and one or more device plugins;
2. watches an upload folder for new files;
3. validates and classifies those files;
4. moves accepted files into record folders;
5. tracks local record upload state;
6. optionally hands record state to a sync backend.

The reference setup uses synthetic plugins on purpose. They make the system
easy to run, test, and extend without bundling real instrument workflows.

## Useful Defaults

This project is Windows-first. The reference configuration assumes normal local
paths:

- watch directory: `Desktop\Upload`
- destination directory: `Desktop\Data`
- app data directory: `C:\Watchdog`

Other useful environment variables:

- `SYNC_BACKEND`: optional, defaults to `noop`
- `PROMETHEUS_PORT`: optional, defaults to `8000`
- `OBSERVABILITY_PORT`: optional, defaults to `8001`

The default `noop` sync backend is offline-safe. If you want the Kadi-backed
sync path, install the optional extra and set the backend explicitly:

```powershell
python -m pip install ".[kadi]"
$env:SYNC_BACKEND = "kadi"
```

## Repo Layout

- [src/d_post](src/d_post/README.md): application code and package map
- [tests](tests): automated tests
- [docs](docs/README.md): maintained documentation map
- [CONTRIBUTING.md](CONTRIBUTING.md): contributor workflow
- [SECURITY.md](SECURITY.md): security reporting guidance

## Development

If you want to work on the code, start with
[CONTRIBUTING.md](CONTRIBUTING.md).

The main checks are:

```powershell
python -m ruff check .
python -m black . --check
python -m pytest
```

## License

`d-post` is released under the MIT License. See [LICENSE](LICENSE).
