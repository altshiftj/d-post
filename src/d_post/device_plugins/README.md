# Device Plugin Guide

Device plugins describe how `d-post` recognizes and processes files for one
kind of data source. A device plugin returns a `DeviceConfig` and a
`FileProcessorABS` implementation.

The public repository intentionally ships synthetic device behavior only. Use
the reference plugin to understand the extension points, not as a model of a
specific real instrument.

## Public Reference Device

| Device plugin | Source | Accepted files | Notes |
| --- | --- | --- | --- |
| `test_device` | [test_device/](test_device/) | `.tif`, `.txt` | Synthetic plugin used by tests and quick-start examples. |

## Files In A Device Plugin

The reference device uses this structure:

```text
src/d_post/device_plugins/
|-- device_plugin.py
`-- test_device/
    |-- __init__.py
    |-- file_processor.py
    |-- plugin.py
    `-- settings.py
```

- `settings.py` builds a `DeviceConfig` with metadata, file selectors, session
  timing, and watcher settings.
- `file_processor.py` implements device-specific processing.
- `plugin.py` registers a concrete `DevicePlugin` implementation.
- `device_plugin.py` defines the public base interface.

## Configuration Responsibilities

`DeviceConfig` is the device-level contract consumed by the runtime:

- `identifier`: plugin identifier used by startup and plugin loading.
- `metadata`: record-facing defaults such as abbreviation, tags, and
  description.
- `files`: selectors used to decide which files or folders belong to the
  device.
- `session`: device-level inactivity timeout.
- `watcher`: stability and retry settings for newly discovered files.
- `extra`: optional plugin-specific settings namespace.

## Processor Responsibilities

A device processor implements `FileProcessorABS`. The main public methods are:

- `device_specific_processing(...)`: move or transform an accepted item into
  the destination record folder and return a `ProcessingOutput`.
- `is_appendable(...)`: decide whether another file can be added to an existing
  local record.
- `matches_file(...)`: perform a lightweight file match when selectors are not
  enough.

The synthetic `test_device` processor moves accepted files verbatim into the
record folder. More advanced public examples should still use fake data,
generic file names, and synthetic metadata.

## Example Registration Shape

```python
from d_post.device_plugins.device_plugin import DevicePlugin
from d_post.plugin_system import hookimpl

from .file_processor import MyFileProcessor
from .settings import build_config


class MyDevicePlugin(DevicePlugin):
    """Synthetic device plugin example."""

    def get_config(self):
        """Return device configuration."""
        return build_config()

    def get_file_processor(self):
        """Return the device processor."""
        return MyFileProcessor()


@hookimpl
def register_device_plugins(registry):
    """Register the synthetic device plugin."""
    registry.register("my_device", MyDevicePlugin)
```

## Related Docs

- [Documentation map](../../../docs/README.md)
- [Source package map](../README.md)
- [PC plugin guide](../pc_plugins/README.md)
