from __future__ import annotations

from urisysedge.runtime import Runtime

import urihim


def test_mouse_status():
    rt = Runtime(config={"him": {"driver": "mock"}})
    urihim.register(rt)
    res = rt.call("him://local/mouse/query/status", {}, {"params": {"host": "local"}})
    assert res["ok"]


def test_click_requires_approval():
    rt = Runtime(config={"him": {"driver": "mock"}})
    urihim.register(rt)
    denied = rt.call("him://local/mouse/command/click", {"x": 1, "y": 2}, {})
    assert not denied["ok"]
    allowed = rt.call("him://local/mouse/command/click", {"x": 1, "y": 2}, {"approved": True})
    assert allowed["ok"]
