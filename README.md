Greetings User, from Tron

# d-post

`d-post` is a Windows desktop app for a repetitive problem: files arrive from
instruments, they need to be recognized, renamed, and moved into a useful
record structure, and doing that by hand is slow and error-prone.

This repo contains the core runtime behind that workflow. It includes the
plugin system, the Tkinter UI, and two small reference plugins,
`test_pc` and `test_device`, so you can run the app and understand how the
pieces fit together without a lot of setup.

## Quick Start

Install the package:

```powershell
python -m pip install .
```

Set the example environment:

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

1. loads a PC plugin and one or more device plugins
2. watches an upload folder for new files
3. validates and classifies those files
4. moves them into record folders
5. optionally hands record state to a sync backend

The reference setup in this repo uses simple fake plugins on purpose. They are
there to make the system easy to run, test, and extend.

## Useful Defaults

This project is Windows-first. The reference configuration assumes normal local
paths:

- watch directory: `Desktop\\Upload`
- destination directory: `Desktop\\Data`
- app data directory: `C:\\Watchdog`

Other useful environment variables:

- `SYNC_BACKEND`: optional, defaults to `noop`
- `PROMETHEUS_PORT`: optional, defaults to `8000`
- `OBSERVABILITY_PORT`: optional, defaults to `8001`

If you want the Kadi-backed sync path, install the optional extra and set the
backend explicitly:

```powershell
python -m pip install ".[kadi]"
$env:SYNC_BACKEND = "kadi"
```

## Repo Layout

- `src/d_post`: application code
- `tests`: automated tests
- `CONTRIBUTING.md`: contributor workflow
- `SECURITY.md`: security reporting guidance

## Development

If you want to work on the code, start with [`CONTRIBUTING.md`](CONTRIBUTING.md).

The main checks are:

```powershell
python -m ruff check .
python -m black .
python -m pytest
```

## License

`d-post` is released under the MIT License. See [`LICENSE`](LICENSE).
