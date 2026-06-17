def register(runtime):
    runtime.register('him://{host}/mouse/query/status', 'python://urihim.handlers:mouse_status', kind='query', operation='him.mouse.status')
    runtime.register('him://{host}/mouse/command/move', 'python://urihim.handlers:mouse_move', kind='command', operation='him.mouse.move', approval='required', side_effects=True)
    runtime.register('him://{host}/mouse/command/click', 'python://urihim.handlers:mouse_click', kind='command', operation='him.mouse.click', approval='required', side_effects=True)
    runtime.register('him://{host}/mouse/command/scroll', 'python://urihim.handlers:mouse_scroll', kind='command', operation='him.mouse.scroll', approval='required', side_effects=True)
    runtime.register('him://{host}/keyboard/command/type', 'python://urihim.handlers:keyboard_type', kind='command', operation='him.keyboard.type', approval='required', side_effects=True)
    runtime.register('him://{host}/keyboard/command/hotkey', 'python://urihim.handlers:keyboard_hotkey', kind='command', operation='him.keyboard.hotkey', approval='required', side_effects=True)
