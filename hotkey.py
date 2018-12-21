# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


# https://github.com/boppreh/keyboard#keyboard.KeyboardEvent


import atexit
import importlib
import keyboard
import operator
import os
import psutil
import pystray
import screeninfo
import signal
import threading
import time
import win32api
import win32com
import win32con
import win32gui
import win32process

from PIL import Image


LAYOUT_PRESET = {
    'windows+keypad5': {
        'landscape': [((1 - v) / 2, 0.00, v, 1.00) for v in (1.00, 0.50, 0.34,)],
        'portrait': [(0.00, (1 - v) / 2, 1.00, v) for v in (1.00, 0.50,)]
    },
    'windows+keypad2': {
        'landscape': [((1 - v) / 2, 0.50, v, 0.50) for v in (1.00, 0.50, 0.34,)],
        'portrait': [(0.00, 1 - v, 1.00, v) for v in (0.75, 0.50, 0.25,)]
    },
    'windows+keypad8': {
        'landscape': [((1 - v) / 2, 0.00, v, 0.50) for v in (1.00, 0.50, 0.34,)],
        'portrait': [(0.00, 0.00, 1.00, v) for v in (0.75, 0.50, 0.25,)]
    },
    'windows+keypad4': {
        'landscape': [(0.00, 0.00, v, 1.00) for v in (0.67, 0.50, 0.33,)],
        'portrait': [(0.00, (1 - v) / 2, 0.50, v) for v in (1.00, 0.50,)]
    },
    'windows+keypad6': {
        'landscape': [(1 - v, 0.00, v, 1.00) for v in (0.67, 0.50, 0.33,)],
        'portrait': [(0.50, (1 - v) / 2, 0.50, v) for v in (1.00, 0.50,)]
    },
    'windows+keypad1': {
        'landscape': [(0.00, 0.50, v, 0.50) for v in (0.67, 0.50, 0.33,)],
        'portrait': [(0.00, 1 - v, 0.50, v) for v in (0.75, 0.50, 0.25,)]
    },
    'windows+keypad3': {
        'landscape': [(1 - v, 0.50, v, 0.50) for v in (0.67, 0.50, 0.33,)],
        'portrait': [(0.50, 1 - v, 0.50, v) for v in (0.75, 0.50, 0.25,)]
    },
    'windows+keypad7': {
        'landscape': [(0.00, 0.00, v, 0.50) for v in (0.67, 0.50, 0.33,)],
        'portrait': [(0.00, 0.00, 0.50, v) for v in (0.75, 0.50, 0.25,)]
    },
    'windows+keypad9': {
        'landscape': [(1 - v, 0.00, v, 0.50) for v in (0.67, 0.50, 0.33,)],
        'portrait': [(0.50, 0.00, 0.50, v) for v in (0.75, 0.50, 0.25,)]
    },
}

HOTKEY_PRESET = {
    'windows+space': {
        'target': {'pname': 'AIMP.exe', 'title': 'TrayControl'},
        'hotkeys': ['space']
    },
    'windows+esc': {
        'target': {'pname': 'AIMP.exe', 'title': 'TrayControl'},
        'hotkeys': ['esc']
    },
    'windows+up': {
        'target': {'pname': 'AIMP.exe', 'title': 'TrayControl'},
        'hotkeys': ['ctrl+up'],
    },
    'windows+down': {
        'target': {'pname': 'AIMP.exe', 'title': 'TrayControl'},
        'hotkeys': ['ctrl+down'],
    },
    'windows+left': {
        'target': {'pname': 'AIMP.exe', 'title': 'TrayControl'},
        'hotkeys': ['left'],
    },
    'windows+right': {
        'target': {'pname': 'AIMP.exe', 'title': 'TrayControl'},
        'hotkeys': ['right'],
    },
    'ctrl+windows+up': {
        'interval': 0.2,
        'target': {'pname': 'AIMP.exe', 'title': 'TrayControl'},
        'hotkeys': ['ctrl+up', 'ctrl+j', '6', '0', 'enter'],
    },
    'ctrl+windows+down': {
        'interval': 0.2,
        'target': {'pname': 'AIMP.exe', 'title': 'TrayControl'},
        'hotkeys': ['ctrl+down', 'ctrl+j', '6', '0', 'enter'],
    },
    # 'ctrl+windows+left': {
    #     'interval': 0.2,
    #     'hotkeys': ['ctrl+windows+left'],
    # },
    # 'ctrl+windows+right': {
    #     'interval': 0.2,
    #     'hotkeys': ['ctrl+windows+right'],
    # },
    # 'ctrl+a': {
    #     'interval': 0.2,
    #     'hotkeys': ['ctrl+a'],
    # },
    # 'ctrl+c': {
    #     'interval': 0.2,
    #     'hotkeys': ['ctrl+c'],
    # },
    # 'ctrl+v': {
    #     'interval': 0.2,
    #     'hotkeys': ['ctrl+v'],
    # },
    # 'ctrl+w': {
    #     'interval': 0.2,
    #     'hotkeys': ['ctrl+w'],
    # },
    # 'ctrl+x': {
    #     'interval': 0.2,
    #     'hotkeys': ['ctrl+x'],
    # },
    # 'ctrl+z': {
    #     'interval': 0.2,
    #     'hotkeys': ['ctrl+z'],
    # },
}


boldendc = ['\033[1m', '\033[0m']
redendc = ['\033[91m', '\033[0m']
blueendc = ['\033[94m', '\033[0m']
grayendc = ['\033[90m', '\033[0m']
boldgrayendc = ['\033[1m' + '\033[90m', '\033[0m']


def sort_preset_hotkey(preset):
    modifiers = sorted(['alt', 'ctrl', 'shift', 'windows'])
    for old_key in preset.keys():
        keys = old_key.split('+')
        mods = [v for v in modifiers if v in keys]
        base = [v for v in keys if v and v not in modifiers]
        new_key = '+'.join(mods + base)
        preset[new_key] = preset.pop(old_key)
    return preset


LAYOUT_PRESET = sort_preset_hotkey(LAYOUT_PRESET)
HOTKEY_PRESET = sort_preset_hotkey(HOTKEY_PRESET)


# class keyboard(keyboard):

#     def __init__(self, *argvs, **kwargs):
#         print(argvs)
#         print(kwargs)
#         super(self.__class__, self).__init__(*argvs, **kwargs)

#     def read_hotkey(suppress=True):
#         """
#         Similar to `read_key()`, but blocks until the user presses and releases a
#         hotkey (or single key), then returns a string representing the hotkey
#         pressed.
#         Example:
#             read_hotkey()
#             # "ctrl+shift+p"
#         """
#         queue = keyboard._queue.Queue()

#         def fn(e):
#             return queue.put(e) or e.event_type == keyboard.KEY_DOWN
#         # fn = lambda e: queue.put(e) or e.event_type == keyboard.KEY_DOWN
#         hooked = keyboard.hook(fn, suppress=suppress)
#         while True:
#             event = queue.get()
#             if event.event_type == keyboard.KEY_UP:
#                 keyboard.unhook(hooked)
#                 with keyboard._pressed_events_lock:
#                     names = [e.name for e in keyboard._pressed_events.values()] + [event.name]
#                 return keyboard.get_hotkey_name(names)


class RepeatHandler():

    def __init__(self, hotkey):
        self.hotkey = hotkey
        self.timestamp = time.time()


class Coordination():

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rectangle():

    def __init__(self, offset_x, offset_y, finish_x, finish_y):
        self.offset = Coordination(offset_x, offset_y)
        self.finish = Coordination(finish_x, finish_y)

    @property
    def width(self):
        return self.finish.x - self.offset.x

    @property
    def height(self):
        return self.finish.y - self.offset.y

    @property
    def orientation(self):
        if self.width > self.height:
            return 'landscape'
        return 'portrait'


class WindowInformation():

    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.title = win32gui.GetWindowText(self.hwnd)
        _, self.pid = win32process.GetWindowThreadProcessId(hwnd)
        self.visible = win32gui.IsWindowVisible(hwnd)
        self.enabled = win32gui.IsWindowEnabled(hwnd)
        # self.owner = win32gui.GetWindow(self.hwnd, win32con.GW_OWNER)
        self.error = False
        # PROCESS_QUERY_INFORMATION (0x0400) or PROCESS_VM_READ (0x0010) or PROCESS_ALL_ACCESS (0x1F0FFF)
        try:
            process = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, self.pid)
            self.pname = win32process.GetModuleFileNameEx(process, 0).split(os.path.sep)[-1]
        except Exception:
            self.pname = ''

        try:
            self.parent = win32gui.GetParent(hwnd)
        except Exception:
            self.error = True


class ForegroundWindowHandler(WindowInformation, Rectangle):

    def __init__(self):
        self.error = False
        for i in range(10):
            hwnd = win32gui.GetForegroundWindow()
            super(self.__class__, self).__init__(hwnd)
            if self.error:
                return
        self.layout_index = 0
        self.refresh()

    def get_screens(self):
        screens = sorted([Rectangle(v.x, v.y, v.x + v.width, v.y + v.height)
                          for v in screeninfo.get_monitors()], key=operator.attrgetter('offset.x'))

        for screen in screens:
            monitor_info = win32api.GetMonitorInfo(
                win32api.MonitorFromPoint((screen.offset.x, screen.offset.y)))

            mx, my, mw, mh = monitor_info.get('Monitor')
            wx, wy, ww, wh = monitor_info.get('Work')

            if mw == ww and wy != my:  # taskbar top
                screen.offset.y += wy - my
            if mw == ww and wy == my:  # taskbar bottom
                screen.finish.y -= mh - wh
            if mh == wh and wx != mx:  # taskbar left
                screen.offset.x += wx - mx
            if mh == wh and wx == mx:  # taskbar right
                screen.finish.x -= mw - ww

        return screens

    def refresh(self):
        self.screens = self.get_screens()
        try:
            rect = win32gui.GetWindowRect(self.hwnd)
            self.title = win32gui.GetWindowText(self.hwnd)
        except Exception:
            self.error = True
            return
        offset_x, offset_y, finish_x, finish_y = rect
        self.offset = Coordination(offset_x, offset_y)
        self.finish = Coordination(finish_x, finish_y)

        for i, screen in enumerate(self.screens):

            offset_x = self.offset.x if self.offset.x > screen.offset.x else screen.offset.x
            offset_y = self.offset.y if self.offset.y > screen.offset.y else screen.offset.y
            finish_x = self.finish.x if self.finish.x < screen.finish.x else screen.finish.x
            finish_y = self.finish.y if self.finish.y < screen.finish.y else screen.finish.y
            screen.index = i

            class Shown():

                def __init__(self, offset_x, offset_y, finish_x, finish_y):
                    self.offset = Coordination(offset_x, offset_y)
                    self.finish = Coordination(finish_x, finish_y)
                    self.width = self.finish.x - self.offset.x
                    self.height = self.finish.y - self.offset.y
                    direction = -1 if self.width < 0 or self.height < 0 else 1
                    self.size = abs(self.width * self.height) * direction

            screen.shown = Shown(offset_x, offset_y, finish_x, finish_y)

        self.screen = sorted(self.screens, key=operator.attrgetter('shown.size'))[-1]

    def get_next_rect(self):

        preset = LAYOUT_PRESET[self.layout_name]
        preset = preset[self.screen.orientation] if isinstance(preset, dict) else preset

        index = self.layout_index + 1
        index = 0 if index > len(preset) - 1 else index
        self.layout_index = index
        xp, yp, wp, hp = preset[index]
        x = self.screen.offset.x + self.screen.width * xp
        y = self.screen.offset.y + self.screen.height * yp
        width = self.screen.width * wp
        height = self.screen.height * hp
        return int(round(x)), int(round(y)), int(round(width)), int(round(height))

    def resize(self, layout_name):
        if not LAYOUT_PRESET.get(layout_name):
            return
        self.layout_name = layout_name
        self.refresh()
        x, y, width, height = self.get_next_rect()
        win32gui.MoveWindow(self.hwnd, x, y, width, height, True)


class HotKeyManager():

    def __init__(self, parent):
        self.windows = []
        self.parent = parent
        self.stopsignal = False

    def get_foreground_window(self):
        hwnd = win32gui.GetForegroundWindow()
        for window in self.windows:
            if window.hwnd == hwnd:
                return window
        for i in range(10):
            window = ForegroundWindowHandler()
            time.sleep(0.05)
            if not window.error:
                self.windows += [window]
                return window
                break

    def get_window_informations(self, refresh=False):

        if not refresh and hasattr(self, '__window_informations_proxy__') \
                and self.__window_informations_timestamp__ + 1.0 > time.time():
            return self.__window_informations_proxy__

        def callback(hwnd, windows):
            window = WindowInformation(hwnd)
            excludes = ('Default IME', 'MSCTFIME UI', 'G',)
            if window.pname and window.title and window.title not in excludes:
                windows += [window]

        windows = []
        win32gui.EnumWindows(callback, windows)
        windows = sorted(windows, key=operator.attrgetter('pid', 'hwnd'))
        self.__window_informations_proxy__ = windows
        self.__window_informations_timestamp__ = time.time()

        if False:
            print('-' * 160)
            for window in windows:
                print(str(window.pid).rjust(6), str(window.hwnd).rjust(8), str(window.parent).rjust(8),
                      window.visible, window.enabled, window.pname.ljust(24), window.title[:100])
            print('-' * 160)
        return windows

    def get_target_window(self, pname=None, title=None):
        for refresh in (False, True,):
            for window in self.get_window_informations(refresh):
                if (pname is None or (pname is not None and pname.lower() == window.pname.lower())) \
                        and (title is None or (title is not None and title.lower() == window.title.lower())):
                    return window

    def handle_hotkey_thread(self):
        while True:
            if self.stopsignal:
                return
            # event = keyboard.read_event(suppress=True)
            # event = keyboard.read_hotkey(suppress=True)
            # print(event)
            # window = self.get_foreground_window()
            # if window and window.pname == 'mstsc.exe' and self.keyboard_binded:
            #     self.unbind_keyboard()
            #     print('keyboard binded')
            # if window and window.pname != 'mstsc.exe' and not self.keyboard_binded:
            #     self.bind_keyboard()
            #     print('keyboard unbinded')
            # self.bind_keyboard()
            time.sleep(3)

    def handle_layout(self, hotkey):
        window = self.get_foreground_window()
        if window:
            window.resize(hotkey)

    def handle_hotkey(self, hotkey):
        preset = HOTKEY_PRESET.get(hotkey)

        # if 'interval' in preset and len(self.eventlogs) > 1 \
        #         and self.eventlogs[0].name == self.eventlogs[1].name \
        #         and self.eventlogs[0].time - self.eventlogs[1].time < preset['interval']:
        #     self.eventlogs.pop(0)
        #     return

        if 'target' in preset:
            origin = self.get_foreground_window()
            target = self.get_target_window(**preset['target'])
            if not origin or not target:
                return
            # print(target.pname, target.title)
            try:
                win32gui.SetForegroundWindow(target.hwnd)
            except Exception:
                print('handle_hotkey(): focusing target failed')
                return
            time.sleep(0.01)

        for hk in preset['hotkeys']:
            if isinstance(hk, str):
                keyboard.send(hk, do_press=True, do_release=True)
            if isinstance(hk, int) or isinstance(hk, float):
                time.sleep(hk)

        if 'target' in preset:
            try:
                win32gui.SetForegroundWindow(origin.hwnd)
            except Exception:
                print('handle_hotkey(): focusing origin failed')
                # print(origin.hwnd, origin.pname, origin.title, origin.pid)

    def keyboard_hook_callback(self, event):
        # print(event.name)

        class EventLog():

            def __init__(self, name):
                self.name = name
                self.time = time.time()

        modifiers = ['alt', 'ctrl', 'shift', 'windows']
        mods = [v for v in sorted(modifiers) if keyboard.is_pressed(v)]
        mods = '+'.join(mods)

        if event.name is None or (not mods and event.event_type == 'up'):
            self.bind_keyboard()
            return
        # if event.name is None or not mods or event.event_type == 'up' or not hasattr(self, 'eventlogs'):
        #     if event.name is None or (not mods and event.event_type == 'up'):
        #         self.bind_keyboard()
        #     self.eventlogs = []
        #     return

        # print(event.event_type)
        if event.event_type == 'down':

            # self.eventlogs.insert(0, EventLog(event.name))
            # self.eventlogs = self.eventlogs[:1000]

            keypad = 'keypad' if event.is_keypad else ''
            hotkey = mods + '+%s' % (keypad + event.name)
            if LAYOUT_PRESET.get(hotkey):
                self.handle_layout(hotkey)
            if HOTKEY_PRESET.get(hotkey):
                self.handle_hotkey(hotkey)

    def suppressed_hotkey_callback(self, input_hotkey):
        print(input_hotkey)
        self.bind_keyboard()
        # print('suppressed_hotkey_callback():', input_hotkey)
        # print(keyboard.is_pressed(input_hotkey))
        # print(keyboard.parse_hotkey(input_hotkey))
        # print(keyboard.parse_hotkey_combinations(input_hotkey))
        # print(sorted(keyboard.sided_modifiers))
        # print(shortcut)
        # class EventLog():

        #     def __init__(self, name):
        #         self.name = name
        #         self.time = time.time()

        # mods = [v for v in sorted(['alt', 'ctrl', 'shift', 'windows']) if keyboard.is_pressed(v)]
        # mods = '+'.join(mods)

        # if not mods or event.event_type == 'up' or not hasattr(self, 'eventlogs'):
        #     # self.bind_keyboard()
        #     self.eventlogs = []

        # if event.event_type == 'down':

        # self.eventlogs.insert(0, EventLog(event.name))
        # self.eventlogs = self.eventlogs[:1000]
        # keys = input_hotkey.split('+')
        # modifiers = ['alt', 'ctrl', 'shift', 'windows']
        # mods = [v for v in sorted(modifiers) if v in keys]
        # key = [v for v in keys if v not in modifiers][0]
        # num = 'num' if key.isdigit() else ''
        # hotkey = '+'.join(mods + [num + key])
        # print(input_hotkey.ljust(20), hotkey)
        # if LAYOUT_PRESET.get(hotkey):
        #     self.handle_layout(hotkey)
        # if HOTKEY_PRESET.get(hotkey):
        #     self.handle_hotkey(hotkey)

    def stop(self, event=None):
        # self.thread.stop()
        self.unbind_keyboard()
        self.stopsignal = True

    def run(self, event=None):
        self.bind_keyboard()
        self.thread = threading.Thread(target=self.handle_hotkey_thread)
        self.thread.daemon = True
        self.thread.start()
        while not self.stopsignal:
            time.sleep(0.1)

    def unbind_keyboard(self):
        keyboard.unhook_all()
        # keyboard.unhook_all_hotkeys()
        self.keyboard_binded = False
        print('unbind_keyboard(): keyboard_unbinded')

    def bind_keyboard(self):
        # importlib.reload(keyboard)
        # self.keyboard = keyboard
        # print(dir(keyboard))
        keyboard.unhook_all()
        # keyboard.unhook_all_hotkeys()

        # for key in [str(v) for v in range(10)]:
        #     keyboard.add_abbreviation(key, 'keypad' + key)

        # keyboard.hook(self.keyboard_hook_callback)

        # for hotkey in [v.replace('keypad', '') for v in list(LAYOUT_PRESET.keys()) + list(HOTKEY_PRESET.keys())]:
        #     keyboard.remove_hotkey(hotkey)

        # keyboard.send('alt+ctrl+shift+windows', do_press=True, do_release=True)
        # for hotkey in [v.replace('keypad', '') for v in list(LAYOUT_PRESET.keys()) + list(HOTKEY_PRESET.keys())]:
        for hotkey in [v.replace('keypad', '') for v in list(LAYOUT_PRESET.keys()) + list(HOTKEY_PRESET.keys())][:1]:
            print(hotkey)
            keyboard.add_hotkey(hotkey, self.suppressed_hotkey_callback, args=(hotkey,),
                                suppress=True, timeout=1, trigger_on_release=False)
        self.keyboard_binded = True
        print('bind_keyboard(): keyboard_binded')


class TrayIcon(pystray.Icon):

    def __init__(self, name='HOTKEY'):
        super(self.__class__, self).__init__(name)
        self.title = name
        self.pid = os.getpid()
        self.cwd = os.path.split(__file__)[0]
        self.handle_existing_instances()
        self.icon = Image.open(os.path.join('assets', 'icon.png'))
        self.menu = pystray.Menu(
            pystray.MenuItem('HOTKEY 0.0.1', lambda item: None),
            pystray.MenuItem('author: Taehong Kim', lambda item: None),
            pystray.MenuItem('email: peppy0510@hotmail.com', lambda item: None),
            pystray.MenuItem('Quit HOTKEY', self.stop, checked=lambda item: True),
        )
        self.visible = True
        self.run()

    def run(self):
        self.hotkey_manager = HotKeyManager(self)
        super(self.__class__, self).run(self.hotkey_manager.run)

    def stop(self, *argvs):
        # if len(argvs):
        self.hotkey_manager.stop()
        self.visible = False
        self._update_icon()
        os.kill(self.pid, signal.SIGTERM)
        super(self.__class__, self).stop()

    def handle_existing_instances(self):
        for p in psutil.process_iter():
            try:
                p.cwd()
            except Exception:
                continue
            if p.pid != self.pid and p.cwd() == self.cwd and p.name() in ('python.exe', 'pythonw.exe',):
                p.terminate()


def main():
    '''
    ABOVE_NORMAL_PRIORITY_CLASS
    BELOW_NORMAL_PRIORITY_CLASS
    HIGH_PRIORITY_CLASS
    IDLE_PRIORITY_CLASS
    NORMAL_PRIORITY_CLASS
    REALTIME_PRIORITY_CLASS
    '''
    p = psutil.Process(os.getpid())
    p.nice(psutil.NORMAL_PRIORITY_CLASS)
    trayicon = TrayIcon()
    atexit.register(trayicon.stop)


if __name__ == '__main__':
    main()
