from __future__ import annotations

import os
import shutil
import subprocess


def _state(context):
    s = context.setdefault('state', {})
    return s.setdefault('him', {'mouse': {'x': 0, 'y': 0}, 'keys': []})


def _real_allowed(context):
    return bool(context.get('allow_real') or os.environ.get('URISYS_ALLOW_REAL') == '1')


def _wayland_session() -> bool:
    return bool(os.environ.get('WAYLAND_DISPLAY'))


def _ydotool_available() -> bool:
    return shutil.which('ydotool') is not None


def _driver(context):
    configured = context.get('config', {}).get('him', {}).get('driver')
    if configured:
        return configured
    env_driver = os.environ.get('URISYS_HIM_DRIVER', '').strip()
    if env_driver:
        return env_driver
    if not _real_allowed(context):
        return 'mock'
    if _wayland_session() and _ydotool_available():
        return 'ydotool'
    return 'pyautogui'


def _pyautogui(context):
    if not _real_allowed(context):
        raise PermissionError('real HIM control requires context.allow_real=true or URISYS_ALLOW_REAL=1')
    try:
        import pyautogui  # type: ignore
        return pyautogui
    except Exception as exc:
        raise RuntimeError('real HIM control requires: pip install pyautogui') from exc


_YDOTOOL_BUTTON = {'left': '0xC0', 'right': '0xC1', 'middle': '0xC2'}
# Linux input event codes (subset) for ydotool key sequences
_YDOTOOL_KEY = {
    'return': 28,
    'enter': 28,
    'tab': 15,
    'escape': 1,
    'esc': 1,
    'space': 57,
    'backspace': 14,
    'ctrl': 29,
    'control': 29,
    'shift': 42,
    'alt': 56,
    'super': 125,
    'meta': 125,
}


def _run_ydotool(context, *args: str) -> None:
    if not _real_allowed(context):
        raise PermissionError('real HIM control requires context.allow_real=true or URISYS_ALLOW_REAL=1')
    if not _ydotool_available():
        raise RuntimeError('real HIM on Wayland requires: apt install ydotool (+ ydotoold)')
    subprocess.run(['ydotool', *args], check=True, capture_output=True, text=True)


def _ydotool_key_sequence(keys: list[str]) -> list[str]:
    """Build ydotool key args: code:1 press, code:0 release (inner keys first)."""
    normalized = [k.strip().lower() for k in keys if k.strip()]
    if not normalized:
        return []
    modifiers = []
    main = normalized[-1]
    for part in normalized[:-1]:
        code = _YDOTOOL_KEY.get(part)
        if code is None:
            raise RuntimeError(f'ydotool hotkey: unknown modifier {part!r}')
        modifiers.append(code)
    main_code = _YDOTOOL_KEY.get(main)
    if main_code is None:
        raise RuntimeError(f'ydotool hotkey: unknown key {main!r}')
    seq: list[str] = []
    for code in modifiers:
        seq.append(f'{code}:1')
    seq.append(f'{main_code}:1')
    seq.append(f'{main_code}:0')
    for code in reversed(modifiers):
        seq.append(f'{code}:0')
    return seq


def mouse_status(payload, context):
    st = _state(context)
    return {'driver': _driver(context), **st['mouse']}


def mouse_move(payload, context):
    x = int(payload.get('x', 0))
    y = int(payload.get('y', 0))
    driver = _driver(context)
    if driver == 'pyautogui':
        if context.get('dry_run'):
            return {'dry_run': True, 'x': x, 'y': y}
        _pyautogui(context).moveTo(x, y)
    elif driver == 'ydotool':
        if context.get('dry_run'):
            return {'dry_run': True, 'x': x, 'y': y, 'driver': driver}
        _run_ydotool(context, 'mousemove', '--absolute', str(x), str(y))
    st = _state(context)
    st['mouse'].update({'x': x, 'y': y})
    return {'x': x, 'y': y, 'driver': driver}


def mouse_click(payload, context):
    x = payload.get('x')
    y = payload.get('y')
    button = payload.get('button', 'left')
    clicks = int(payload.get('clicks', 1))
    driver = _driver(context)
    if driver == 'pyautogui':
        if context.get('dry_run'):
            return {'dry_run': True, 'x': x, 'y': y, 'button': button, 'clicks': clicks}
        pg = _pyautogui(context)
        if x is not None and y is not None:
            pg.click(int(x), int(y), clicks=clicks, button=button)
        else:
            pg.click(clicks=clicks, button=button)
    elif driver == 'ydotool':
        if context.get('dry_run'):
            return {'dry_run': True, 'x': x, 'y': y, 'button': button, 'clicks': clicks, 'driver': driver}
        if x is not None and y is not None:
            _run_ydotool(context, 'mousemove', '--absolute', str(int(x)), str(int(y)))
        code = _YDOTOOL_BUTTON.get(button, _YDOTOOL_BUTTON['left'])
        for _ in range(clicks):
            _run_ydotool(context, 'click', code)
    st = _state(context)
    if x is not None and y is not None:
        st['mouse'].update({'x': int(x), 'y': int(y)})
    return {'clicked': True, 'x': st['mouse']['x'], 'y': st['mouse']['y'], 'button': button, 'clicks': clicks, 'driver': driver}


def keyboard_type(payload, context):
    text = payload.get('text', '')
    driver = _driver(context)
    if driver == 'pyautogui':
        if context.get('dry_run'):
            return {'dry_run': True, 'text': text}
        _pyautogui(context).write(text)
    elif driver == 'ydotool':
        if context.get('dry_run'):
            return {'dry_run': True, 'text': text, 'driver': driver}
        _run_ydotool(context, 'type', text)
    _state(context)['keys'].append({'type': 'text', 'text': text})
    return {'typed': text, 'chars': len(text), 'driver': driver}


def keyboard_hotkey(payload, context):
    keys = payload.get('keys', [])
    if isinstance(keys, str):
        keys = [k.strip() for k in keys.split('+') if k.strip()]
    driver = _driver(context)
    if driver == 'pyautogui':
        if context.get('dry_run'):
            return {'dry_run': True, 'keys': keys}
        _pyautogui(context).hotkey(*keys)
    elif driver == 'ydotool':
        if context.get('dry_run'):
            return {'dry_run': True, 'keys': keys, 'driver': driver}
        seq = _ydotool_key_sequence(keys)
        _run_ydotool(context, 'key', *seq)
    _state(context)['keys'].append({'type': 'hotkey', 'keys': keys})
    return {'hotkey': keys, 'driver': driver}
