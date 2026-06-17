import urihim.handlers as him


def test_mouse_scroll_dry_run_mock():
    out = him.mouse_scroll({'amount': -5}, {'dry_run': True, 'allow_real': True})
    assert out['dry_run'] is True
    assert out['amount'] == -5


def test_mouse_scroll_dry_run_ydotool():
    ctx = {'dry_run': True, 'allow_real': True, 'config': {'him': {'driver': 'ydotool'}}}
    out = him.mouse_scroll({'amount': 3, 'x': 100, 'y': 200}, ctx)
    assert out['dry_run'] is True
    assert out['driver'] == 'ydotool'
