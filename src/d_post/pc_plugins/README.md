# PC Plugin Guide

PC plugins provide workstation-level configuration for `d-post`. A PC plugin
returns a `PCConfig` object that selects active device plugins and can override
filesystem, naming, session, and watcher defaults.

`d-post` loads exactly one PC plugin at startup, based on the `PC_NAME`
environment variable. If `DEVICE_PLUGINS` is unset, startup reads
`PCConfig.active_device_plugins` from the selected PC plugin.

## Public Reference Profile

| PC plugin | Source | Active device plugins | Notes |
| --- | --- | --- | --- |
| `test_pc` | [test_pc/](test_pc/) | `test_device` | Synthetic profile used by tests and quick-start examples. |

## Files In A PC Plugin

The reference profile uses this structure:

```text
src/d_post/pc_plugins/
|-- pc_plugin.py
`-- test_pc/
    |-- __init__.py
    |-- plugin.py
    `-- settings.py
```

- `settings.py` builds and returns a `PCConfig`.
- `plugin.py` registers a concrete `PCPlugin` implementation.
- `PCConfig.active_device_plugins` lists device plugin identifiers that should
  run with this PC profile when `DEVICE_PLUGINS` is not set.

## Example Shape

```python
from d_post.core.config import PCConfig, PathSettings
from d_post.pc_plugins.pc_plugin import PCPlugin
from d_post.plugin_system import hookimpl


def build_config() -> PCConfig:
    """Build a synthetic PC profile."""
    paths = PathSettings()
    return PCConfig(
        identifier="my_pc",
        name="My Synthetic PC",
        paths=paths,
        active_device_plugins=("my_device",),
    )


class MyPCPlugin(PCPlugin):
    """Return the synthetic PC profile configuration."""

    def get_config(self) -> PCConfig:
        """Return this PC profile's configuration."""
        return build_config()


@hookimpl
def register_pc_plugins(registry):
    """Register the synthetic PC plugin."""
    registry.register("my_pc", MyPCPlugin)
```

## Troubleshooting

- `No PC plugin named '<value>'`: confirm `PC_NAME` matches the identifier
  passed to `registry.register()`.
- Devices missing at runtime: ensure `PCConfig.active_device_plugins` lists the
  intended device identifiers, or set `DEVICE_PLUGINS` explicitly.
- Custom paths not respected: verify the plugin modifies `PathSettings` before
  returning `PCConfig`.

## Related Docs

- [Documentation map](../../../docs/README.md)
- [Source package map](../README.md)
- [Device plugin guide](../device_plugins/README.md)
