# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


# https://github.com/boppreh/keyboard#keyboard.KeyboardEvent


import keyboard
import operator
import os
import psutil
import pystray
import screeninfo
import setproctitle
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
    'windows+num5': {
        'landscape': [((1 - v) / 2, 0.00, v, 1.00) for v in (1.00, 0.50, 0.34,)],
        'portrait': [(0.00, (1 - v) / 2, 1.00, v) for v in (1.00, 0.50,)]
    },
    'windows+num2': {
        'landscape': [((1 - v) / 2, 0.50, v, 0.50) for v in (1.00, 0.50, 0.34,)],
        'portrait': [(0.00, 1 - v, 1.00, v) for v in (0.75, 0.50, 0.25,)]
    },
    'windows+num8': {
        'landscape': [((1 - v) / 2, 0.00, v, 0.50) for v in (1.00, 0.50, 0.34,)],
        'portrait': [(0.00, 0.00, 1.00, v) for v in (0.75, 0.50, 0.25,)]
    },
    'windows+num4': {
        'landscape': [(0.00, 0.00, v, 1.00) for v in (0.67, 0.50, 0.33,)],
        'portrait': [(0.00, (1 - v) / 2, 0.50, v) for v in (1.00, 0.50,)]
    },
    'windows+num6': {
        'landscape': [(1 - v, 0.00, v, 1.00) for v in (0.67, 0.50, 0.33,)],
        'portrait': [(0.50, (1 - v) / 2, 0.50, v) for v in (1.00, 0.50,)]
    },
    'windows+num1': {
        'landscape': [(0.00, 0.50, v, 0.50) for v in (0.67, 0.50, 0.33,)],
        'portrait': [(0.00, 1 - v, 0.50, v) for v in (0.75, 0.50, 0.25,)]
    },
    'windows+num3': {
        'landscape': [(1 - v, 0.50, v, 0.50) for v in (0.67, 0.50, 0.33,)],
        'portrait': [(0.50, 1 - v, 0.50, v) for v in (0.75, 0.50, 0.25,)]
    },
    'windows+num7': {
        'landscape': [(0.00, 0.00, v, 0.50) for v in (0.67, 0.50, 0.33,)],
        'portrait': [(0.00, 0.00, 0.50, v) for v in (0.75, 0.50, 0.25,)]
    },
    'windows+num9': {
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
    'ctrl+windows+left': {
        'interval': 0.2,
        'hotkeys': ['ctrl+windows+left'],
    },
    'ctrl+windows+right': {
        'interval': 0.2,
        'hotkeys': ['ctrl+windows+right'],
    },
}


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
        # PROCESS_QUERY_INFORMATION (0x0400) or PROCESS_VM_READ (0x0010) or PROCESS_ALL_ACCESS (0x1F0FFF)
        try:
            process = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, self.pid)
            self.pname = win32process.GetModuleFileNameEx(process, 0).split(os.path.sep)[-1]
        except Exception:
            self.pname = ''

        try:
            self.parent = win32gui.GetParent(hwnd)
        except Exception:
            pass
            # self.parent = None


class ForegroundWindowHandler(WindowInformation, Rectangle):

    def __init__(self):
        for i in range(10):
            hwnd = win32gui.GetForegroundWindow()
            super(self.__class__, self).__init__(hwnd)
            if hasattr(self, 'parent'):
                break
            else:
                time.sleep(0.05)

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
        rect = win32gui.GetWindowRect(self.hwnd)
        self.title = win32gui.GetWindowText(self.hwnd)
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

    def __init__(self):
        self.windows = []

    def get_foreground_window(self):
        hwnd = win32gui.GetForegroundWindow()
        for window in self.windows:
            if window.hwnd == hwnd:
                return window
        window = ForegroundWindowHandler()
        self.windows += [window]
        return window

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
            time.sleep(0.01)

    def handle_layout(self, hotkey):
        window = self.get_foreground_window()
        window.resize(hotkey)

    def handle_hotkey(self, hotkey):

        preset = HOTKEY_PRESET.get(hotkey)

        if 'interval' in preset and len(self.eventlogs) > 1 \
                and self.eventlogs[0].name == self.eventlogs[1].name \
                and self.eventlogs[0].time - self.eventlogs[1].time < preset['interval']:
            self.eventlogs.pop(0)
            return

        if 'target' in preset:
            origin = self.get_foreground_window()
            target = self.get_target_window(**preset['target'])
            if not target:
                return
            # print(target.pname, target.title)
            try:
                win32gui.SetForegroundWindow(target.hwnd)
            except Exception:
                print('focusing target failed')
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
                print('focusing origin failed')
                # print(origin.hwnd, origin.pname, origin.title, origin.pid)

    def keyboard_hook_callback(self, event):
        # print(event.name)

        class EventLog():

            def __init__(self, name):
                self.name = name
                self.time = time.time()

        mods = [v for v in sorted(['alt', 'ctrl', 'shift', 'windows']) if keyboard.is_pressed(v)]
        mods = '+'.join(mods)

        if not mods or event.event_type == 'up' or not hasattr(self, 'eventlogs'):
            # self.bind_keyboard()
            self.eventlogs = []

        if event.event_type == 'down':

            self.eventlogs.insert(0, EventLog(event.name))
            self.eventlogs = self.eventlogs[:1000]

            num = 'num' if event.is_keypad else ''
            hotkey = mods + '+%s' % (num + event.name)
            if LAYOUT_PRESET.get(hotkey):
                self.handle_layout(hotkey)
            if HOTKEY_PRESET.get(hotkey):
                self.handle_hotkey(hotkey)

    def suppressed_hotkey_callback(self, hotkey):
        pass

    def handle_existing_instances(self):
        pid = os.getpid()
        cwd = os.path.split(__file__)[0]
        processes = []
        for p in psutil.process_iter():
            try:
                p.cwd()
            except Exception:
                continue
            processes += [{'pid': p.pid, 'cwd': p.cwd(), 'name': p.name()}]
        processes = sorted(processes, key=operator.itemgetter('cwd'))

        if False:
            print('-' * 120)
            for p in processes:
                print(str(p['pid']).rjust(6), p['cwd'].ljust(64), p['name'].ljust(6))
            print('-' * 120)
            print(str(pid).rjust(6))
            print('-' * 120)

        for p in processes:
            if p['pid'] != pid and p['cwd'] == cwd and p['name'] in ('python.exe', 'pythonw.exe',):
                os.kill(p['pid'], signal.SIGINT)

    def run(self):
        self.handle_existing_instances()
        self.bind_keyboard()
        # self.handle_hotkey_thread = threading.Thread(target=self.handle_hotkey_thread)
        # self.handle_hotkey_thread.daemon = True
        # self.handle_hotkey_thread.start()

        while True:
            time.sleep(0.1)

    def bind_keyboard(self):
        keyboard.unhook_all()
        keyboard.hook(self.keyboard_hook_callback)
        keyboard.send('alt+ctrl+shift+windows', do_press=True, do_release=True)
        for hotkey in [v.replace('num', '') for v in list(LAYOUT_PRESET.keys()) + list(HOTKEY_PRESET.keys())]:
            keyboard.add_hotkey(hotkey, self.suppressed_hotkey_callback, args=(hotkey,),
                                suppress=True, timeout=1, trigger_on_release=False)
            keyboard.add_hotkey(hotkey, self.suppressed_hotkey_callback, args=(hotkey,),
                                suppress=True, timeout=1, trigger_on_release=True)


def stop():
    icon.visible = False
    icon.stop()
    pid = os.getpid()
    os.kill(pid, signal.SIGINT)


trayicon = Image.open(os.path.join('assets', 'icon.png'))
icon = pystray.Icon('HOTKEY', trayicon, 'HOTKEY')
icon.menu = pystray.Menu(
    pystray.MenuItem('HOTKEY 0.0.1', lambda item: None),
    pystray.MenuItem('author: Taehong Kim', lambda item: None),
    pystray.MenuItem('email: peppy0510@hotmail.com', lambda item: None),
    pystray.MenuItem('Quit HOTKEY', stop, checked=lambda item: True),
)
icon.visible = True


def hotkey_manager(event):
    manager = HotKeyManager()
    manager.run()


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
    p.nice(psutil.HIGH_PRIORITY_CLASS)
    icon.run(hotkey_manager)


if __name__ == '__main__':
    main()
