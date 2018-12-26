# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


# https://github.com/boppreh/keyboard#keyboard.KeyboardEvent


from keyboard import *  # noqa
from keyboard import KEY_DOWN
from keyboard import KEY_UP
from keyboard import _State
from keyboard import _add_hotkey_step
from keyboard import _listener
from keyboard import _logically_pressed_keys
from keyboard import _pressed_events
from keyboard import _pressed_events_lock
from keyboard import _queue
from keyboard import _time
from keyboard import get_hotkey_name
from keyboard import hook
from keyboard import is_pressed
from keyboard import parse_hotkey_combinations
from keyboard import press
from keyboard import release
from keyboard import unhook


def read_hotkey(suppress=True):
    """
    Similar to `read_key()`, but blocks until the user presses and releases a
    hotkey (or single key), then returns a string representing the hotkey
    pressed.
    Example:
        read_hotkey()
        # "ctrl+shift+p"
    """
    queue = _queue.Queue()
    hooked = hook(lambda e: queue.put(e) or e.event_type == KEY_DOWN, suppress=suppress)
    while True:
        event = queue.get()
        if event.event_type == KEY_UP:
            unhook(hooked)
            with _pressed_events_lock:
                names = [e.name for e in _pressed_events.values()] + [event.name]
            return get_hotkey_name(names)


_hotkeys = {}

_last_downed_hotkeys = []


def add_hotkey(hotkey, callback, args=(), suppress=False, timeout=1, trigger_on_release=False):
    """
    Invokes a callback every time a hotkey is pressed. The hotkey must
    be in the format `ctrl+shift+a, s`. This would trigger when the user holds
    ctrl, shift and "a" at once, releases, and then presses "s". To represent
    literal commas, pluses, and spaces, use their names ('comma', 'plus',
    'space').
    - `args` is an optional list of arguments to passed to the callback during
    each invocation.
    - `suppress` defines if successful triggers should block the keys from being
    sent to other programs.
    - `timeout` is the amount of seconds allowed to pass between key presses.
    - `trigger_on_release` if true, the callback is invoked on key release instead
    of key press.
    The event handler function is returned. To remove a hotkey call
    `remove_hotkey(hotkey)` or `remove_hotkey(handler)`.
    before the hotkey state is reset.
    Note: hotkeys are activated when the last key is *pressed*, not released.
    Note: the callback is executed in a separate thread, asynchronously. For an
    example of how to use a callback synchronously, see `wait`.
    Examples:
        # Different but equivalent ways to listen for a spacebar key press.
        add_hotkey(' ', print, args=['space was pressed'])
        add_hotkey('space', print, args=['space was pressed'])
        add_hotkey('Space', print, args=['space was pressed'])
        # Here 57 represents the keyboard code for spacebar; so you will be
        # pressing 'spacebar', not '57' to activate the print function.
        add_hotkey(57, print, args=['space was pressed'])
        add_hotkey('ctrl+q', quit)
        add_hotkey('ctrl+alt+enter, space', some_callback)
    """

    # if args:
    #     def callback(args):
    #         return callback(*args)

    #     # callback = lambda callback=callback: callback(*args)

    _listener.start_if_necessary()

    steps = parse_hotkey_combinations(hotkey)

    event_type = KEY_UP if trigger_on_release else KEY_DOWN
    if len(steps) == 1:
        # Deciding when to allow a KEY_UP event is far harder than I thought,
        # and any mistake will make that key "sticky". Therefore just let all
        # KEY_UP events go through as long as that's not what we are listening
        # for.
        def handler(e):
            # if e.is_keypad() and set(args[0].split('+')).intersection({'up', 'down', 'left', 'right'}):
            #     return 4
            keys = hotkey.split('+')
            hasdigit = bool([key for key in keys if key.isdigit()])
            hasarrow = bool(set(keys).intersection({'up', 'down', 'left', 'right'}))
            # print(steps, event_type)

            # if (hasarrow and e.is_keypad) or (not hasdigit and not e.is_keypad):
            # if hasarrow and e.is_keypad:
            # print(str(int(is_pressed(keys[-1]))).rjust(16), int(e.is_keypad), str(e.time).split('.')[-1][-4:])
            if is_pressed(hotkey) and (
                    (hasdigit and e.is_keypad)
                    or (hasarrow and not e.is_keypad)
                    or (not hasdigit and not hasarrow)
            ):
                return (event_type == KEY_DOWN and e.event_type == KEY_UP and e.scan_code in _logically_pressed_keys) or (
                    event_type == e.event_type and callback(*args, event=e))

            # if _last_downed_hotkeys

            # _last_downed_hotkeys += [args[0]]

            # print(args[0], e.time)

            # return (event_type == KEY_DOWN and e.event_type == KEY_UP and e.scan_code in _logically_pressed_keys) or (
            #     event_type == e.event_type and callback(*args, event=e))

        # handler = lambda e: (event_type == KEY_DOWN and e.event_type == KEY_UP and e.scan_code in _logically_pressed_keys) or (
        #     event_type == e.event_type and callback())4
        remove_step = _add_hotkey_step(handler, steps[0], suppress)

        def remove_():
            remove_step()
            del _hotkeys[hotkey]
            del _hotkeys[remove_]
            del _hotkeys[callback]
        # TODO: allow multiple callbacks for each hotkey without overwriting the
        # remover.
        _hotkeys[hotkey] = _hotkeys[remove_] = _hotkeys[callback] = remove_
        return remove_

    state = _State()
    state.remove_catch_misses = None
    state.remove_last_step = None
    state.suppressed_events = []
    state.last_update = float('-inf')

    def catch_misses(event, force_fail=False):
        if (
                event.event_type == event_type
                and state.index
                and event.scan_code not in allowed_keys_by_step[state.index]
            ) or (
                timeout
                and _time.monotonic() - state.last_update >= timeout
        ) or force_fail:  # Weird formatting to ensure short-circuit.

            state.remove_last_step()

            for event in state.suppressed_events:
                if event.event_type == KEY_DOWN:
                    press(event.scan_code)
                else:
                    release(event.scan_code)
            del state.suppressed_events[:]

            # index = 0
            set_index(0)
        return True

    def set_index(new_index):

        state.index = new_index

        if new_index == 0:
            # This is done for performance reasons, avoiding a global key hook
            # that is always on.
            state.remove_catch_misses = lambda: None
        elif new_index == 1:
            state.remove_catch_misses()
            # Must be `suppress=True` to ensure `send` has priority.
            state.remove_catch_misses = hook(catch_misses, suppress=True)

        if new_index == len(steps) - 1:
            def handler(event):
                if event.event_type == KEY_UP:
                    remove()
                    set_index(0)
                accept = event.event_type == event_type and callback()
                if accept:
                    return catch_misses(event, force_fail=True)
                else:
                    state.suppressed_events[:] = [event]
                    return False
            remove = _add_hotkey_step(handler, steps[state.index], suppress)
        else:
            # Fix value of next_index.
            def handler(event, new_index=state.index + 1):
                if event.event_type == KEY_UP:
                    remove()
                    set_index(new_index)
                state.suppressed_events.append(event)
                return False
            remove = _add_hotkey_step(handler, steps[state.index], suppress)
        state.remove_last_step = remove
        state.last_update = _time.monotonic()
        return False
    set_index(0)

    allowed_keys_by_step = [
        set().union(*step)
        for step in steps
    ]

    def remove_():
        state.remove_catch_misses()
        state.remove_last_step()
        del _hotkeys[hotkey]
        del _hotkeys[remove_]
        del _hotkeys[callback]
    # TODO: allow multiple callbacks for each hotkey without overwriting the
    # remover.
    _hotkeys[hotkey] = _hotkeys[remove_] = _hotkeys[callback] = remove_
    return remove_


register_hotkey = add_hotkey


def unhook_all_hotkeys():
    """
    Removes all keyboard hotkeys in use, including abbreviations, word listeners,
    `record`ers and `wait`s.
    """
    # Because of "alises" some hooks may have more than one entry, all of which
    # are removed together.
    _listener.blocking_hotkeys.clear()
    _listener.nonblocking_hotkeys.clear()


unregister_all_hotkeys = remove_all_hotkeys = clear_all_hotkeys = unhook_all_hotkeys
