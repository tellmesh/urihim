from __future__ import annotations

from importlib.resources import as_file

from uri_control import CapabilityRegistry

import urihim


def test_manifest_loads():
    with as_file(urihim.manifest_path()) as path:
        registry = CapabilityRegistry.from_manifest_files([path])
    assert registry.manifests[0].scheme == "him"
    assert len(registry.routes) == 6
    ops = {route.operation for route in registry.routes}
    assert "him.mouse.scroll" in ops
    assert "him.keyboard.hotkey" in ops
