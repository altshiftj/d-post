"""Test device plugin wiring used for automated verification suites."""

from __future__ import annotations

from typing import TYPE_CHECKING

from d_post.core.config import DeviceConfig
from d_post.device_plugins.device_plugin import DevicePlugin
from d_post.device_plugins.test_device.file_processor import TestFileProcessor
from d_post.device_plugins.test_device.settings import build_config
from d_post.plugin_system import hookimpl

if TYPE_CHECKING:
    from d_post.plugin_system import DevicePluginRegistry


class TestDevicePlugin(DevicePlugin):
    """Test device plugin for unit and integration testing."""

    __test__ = False  # Prevent pytest from collecting this plugin class as a test.

    def __init__(self) -> None:
        self._config = build_config()
        self._file_processor = TestFileProcessor(device_config=self._config)

    def get_config(self) -> DeviceConfig:
        return self._config

    def get_file_processor(self) -> TestFileProcessor:
        return self._file_processor


@hookimpl
def register_device_plugins(registry: "DevicePluginRegistry") -> None:
    registry.register("test_device", TestDevicePlugin)
