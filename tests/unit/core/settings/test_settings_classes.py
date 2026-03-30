import pytest

from d_post.pc_plugins.test_pc.settings import build_config as build_pc_config
from d_post.device_plugins.test_device.settings import (
    build_config as build_device_config,
)


@pytest.mark.parametrize(
    "extractor, expected",
    [
        pytest.param(lambda cfg: cfg.identifier, "test_pc", id="identifier"),
        pytest.param(
            lambda cfg: cfg.active_device_plugins, ("test_device",), id="devices"
        ),
        pytest.param(lambda cfg: cfg.paths.watch_dir.name, "Upload", id="watch-dir"),
        pytest.param(lambda cfg: cfg.naming.id_separator, "-", id="id-separator"),
    ],
)
def test_pc_config_defaults(extractor, expected):
    config = build_pc_config()
    assert extractor(config) == expected


@pytest.mark.parametrize(
    "extractor, expected",
    [
        pytest.param(lambda cfg: cfg.identifier, "test_device", id="identifier"),
        pytest.param(
            lambda cfg: ".tif" in cfg.files.allowed_extensions, True, id="extension"
        ),
        pytest.param(lambda cfg: cfg.metadata.device_abbr, "TEST", id="abbr"),
        pytest.param(
            lambda cfg: cfg.metadata.user_kadi_id,
            "undefined-device-user",
            id="user-kadi-id",
        ),
        pytest.param(
            lambda cfg: cfg.metadata.user_persistent_id,
            -1,
            id="user-persistent-id",
        ),
        pytest.param(
            lambda cfg: cfg.metadata.record_kadi_id,
            "udr_01",
            id="record-kadi-id",
        ),
        pytest.param(
            lambda cfg: cfg.metadata.record_persistent_id,
            -1,
            id="record-persistent-id",
        ),
    ],
)
def test_device_config_defaults(extractor, expected):
    config = build_device_config()
    assert extractor(config) == expected
