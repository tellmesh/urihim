from __future__ import annotations
import os


def _state(context):
    s = context.setdefault('state', {})
    return s.setdefault('him', {'mouse': {'x': 0, 'y': 0}, 'keys': []})


def _driver(context):
    return context.get('config', {}).get('him', {}).get('driver', 'mock')


def _real_allowed(context):
    return bool(context.get('allow_real') or os.environ.get('URISYS_ALLOW_REAL') == '1')


def _pyautogui(context):
    if not _real_allowed(context):
        raise PermissionError('real HIM control requires context.allow_real=true or URISYS_ALLOW_REAL=1')
    try:
        import pyautogui  # type: ignore
        return pyautogui
    except Exception as exc:
        raise RuntimeError('real HIM control requires: pip install pyautogui') from exc


def mouse_status(payload, context):
    st = _state(context)
    return {'driver': _driver(context), **st['mouse']}


def mouse_move(payload, context):
    x = int(payload.get('x', 0)); y = int(payload.get('y', 0))
    if _driver(context) == 'pyautogui':
        if context.get('dry_run'):
            return {'dry_run': True, 'x': x, 'y': y}
        _pyautogui(context).moveTo(x, y)
    st = _state(context)
    st['mouse'].update({'x': x, 'y': y})
    return {'x': x, 'y': y, 'driver': _driver(context)}


def mouse_click(payload, context):
    x = payload.get('x'); y = payload.get('y')
    button = payload.get('button', 'left')
    clicks = int(payload.get('clicks', 1))
    if _driver(context) == 'pyautogui':
        if context.get('dry_run'):
            return {'dry_run': True, 'x': x, 'y': y, 'button': button, 'clicks': clicks}
        pg = _pyautogui(context)
        if x is not None and y is not None:
            pg.click(int(x), int(y), clicks=clicks, button=button)
        else:
            pg.click(clicks=clicks, button=button)
    st = _state(context)
    if x is not None and y is not None:
        st['mouse'].update({'x': int(x), 'y': int(y)})
    return {'clicked': True, 'x': st['mouse']['x'], 'y': st['mouse']['y'], 'button': button, 'clicks': clicks}


def keyboard_type(payload, context):
    text = payload.get('text', '')
    if _driver(context) == 'pyautogui':
        if context.get('dry_run'):
            return {'dry_run': True, 'text': text}
        _pyautogui(context).write(text)
    _state(context)['keys'].append({'type': 'text', 'text': text})
    return {'typed': text, 'chars': len(text)}


def keyboard_hotkey(payload, context):
    keys = payload.get('keys', [])
    if isinstance(keys, str):
        keys = [k.strip() for k in keys.split('+') if k.strip()]
    if _driver(context) == 'pyautogui':
        if context.get('dry_run'):
            return {'dry_run': True, 'keys': keys}
        _pyautogui(context).hotkey(*keys)
    _state(context)['keys'].append({'type': 'hotkey', 'keys': keys})
    return {'hotkey': keys}
