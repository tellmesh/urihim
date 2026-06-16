import os
from unittest import mock

import urihim.handlers as him


def test_driver_mock_without_allow_real():
    assert him._driver({}) == 'mock'


def test_driver_configured():
    ctx = {'config': {'him': {'driver': 'ydotool'}}, 'allow_real': True}
    assert him._driver(ctx) == 'ydotool'


def test_driver_env_override():
    ctx = {'allow_real': True}
    with mock.patch.dict(os.environ, {'URISYS_HIM_DRIVER': 'mock'}):
        assert him._driver(ctx) == 'mock'


def test_driver_wayland_prefers_ydotool():
    ctx = {'allow_real': True}
    with mock.patch.dict(os.environ, {'WAYLAND_DISPLAY': 'wayland-0'}, clear=False):
        with mock.patch.object(him, '_ydotool_available', return_value=True):
            assert him._driver(ctx) == 'ydotool'


def test_driver_x11_defaults_pyautogui():
    ctx = {'allow_real': True}
    env = {k: v for k, v in os.environ.items() if k != 'WAYLAND_DISPLAY' and k != 'URISYS_HIM_DRIVER'}
    with mock.patch.dict(os.environ, env, clear=True):
        assert him._driver(ctx) == 'pyautogui'


def test_ydotool_key_sequence_ctrl_enter():
    seq = him._ydotool_key_sequence(['ctrl', 'Return'])
    assert seq == ['29:1', '28:1', '28:0', '29:0']
