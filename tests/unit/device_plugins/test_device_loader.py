from __future__ import annotations

import pytest

from d_post.core.config import DeviceConfig
from d_post.device_plugins.device_plugin import DevicePlugin
from d_post.loader import load_device_plugin


def _load_device_or_skip(name: str) -> DevicePlugin:
    """Load a device plugin or skip when the curated export does not ship it."""
    try:
        return load_device_plugin(name)
    except RuntimeError as exc:
        pytest.skip(f"Device plugin {name!r} not available: {exc}")


@pytest.mark.parametrize(
    ("device_name", "expectations"),
    [
        (
            "test_device",
            {
                "identifier": "test_device",
                "native_ext": {".tif"},
                "device_abbr": "TEST",
            },
        ),
    ],
)
def test_load_device_plugins(device_name: str, expectations: dict[str, object]) -> None:
    """Load the public reference device plugin exposed by the export."""
    plugin = _load_device_or_skip(device_name)
    assert isinstance(plugin, DevicePlugin)

    config = plugin.get_config()
    assert isinstance(config, DeviceConfig)

    if "identifier" in expectations:
        assert config.identifier == expectations["identifier"]
    if "native_ext" in expectations:
        assert expectations["native_ext"].issubset(set(config.files.native_extensions))
    if "device_abbr" in expectations:
        assert config.metadata.device_abbr == expectations["device_abbr"]


def test_device_plugin_not_found() -> None:
    """Raise a runtime error for unknown device plugins."""
    with pytest.raises(RuntimeError, match="No device plugin named 'ghost_device'"):
        load_device_plugin("ghost_device")
