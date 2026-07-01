# d-post Documentation Map

This index is the front door for maintained project documentation. It points to
current reference pages and keeps public docs separate from implementation
history.

## Which Doc Should I Read?

| Audience | Start here | Then read |
| --- | --- | --- |
| New users | [Root README](../README.md) | Quick start, useful defaults, and repository layout. |
| Contributors | [Contributing guide](../CONTRIBUTING.md) | Test commands, development setup, and PR expectations. |
| Source readers | [Source package map](../src/d_post/README.md) | Runtime package layout and core modules. |
| PC plugin authors | [PC plugin guide](../src/d_post/pc_plugins/README.md) | Workstation configuration and active device selection. |
| Device plugin authors | [Device plugin guide](../src/d_post/device_plugins/README.md) | Device metadata, selectors, and processing contracts. |
| Security reporters | [Security policy](../SECURITY.md) | Responsible vulnerability reporting. |

## Current Reference

- [Root README](../README.md)
- [Contributing guide](../CONTRIBUTING.md)
- [Security policy](../SECURITY.md)
- [Source package map](../src/d_post/README.md)
- [PC plugin guide](../src/d_post/pc_plugins/README.md)
- [Device plugin guide](../src/d_post/device_plugins/README.md)

## Reference Plugin Setup

The public repository intentionally ships synthetic plugins:

- `test_pc`: a PC profile that selects the synthetic device plugin.
- `test_device`: a device plugin that accepts `.tif` and `.txt` files and moves
  them into local record folders.

These plugins are examples for contributors and plugin authors. They are not
intended to model a specific real instrument.

## Documentation Rules

- Keep examples synthetic and public-safe.
- Prefer Windows PowerShell commands unless a page explicitly covers another
  environment.
- Keep Kadi usage optional and clearly marked as requiring `d-post[kadi]`.
- Keep source links aligned with `src/d_post`, not private package names.
