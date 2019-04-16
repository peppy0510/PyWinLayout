# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


# https://github.com/boppreh/keyboard#keyboard.KeyboardEvent


import atexit
import ctypes
import importlib
import keyboardex as keyboard
import mido
import operator
import os
import psutil
import pystray
import screeninfo
import signal
import subprocess
import sys
import threading
import time
import uiautomation
import win32api
import win32com
import win32con
import win32gui
import win32process
import wx
import wx.adv

from PIL import Image
from preset import LAYOUT_PRESET


HOTKEY_PRESET = {
    'windows+space': {
        'target': {'pname': 'AIMP.exe', 'title': 'TrayControl'},
        'hotkeys': ['space']
    },
    'windows+esc': {
        'target': {'pname': 'AIMP.exe', 'title': 'TrayControl'},
        'hotkeys': ['esc']
    },
    # 'windows+up': {
    #     'target': {'pname': 'AIMP.exe'},
    #     'hotkeys': ['ctrl+up'],
    # },
    # 'windows+down': {
    #     'target': {'pname': 'AIMP.exe'},
    #     'hotkeys': ['ctrl+down'],
    # },
    # 'windows+left': {
    #     'target': {'pname': 'AIMP.exe'},
    #     'hotkeys': ['left'],
    # },
    # 'windows+right': {
    #     'target': {'pname': 'AIMP.exe'},
    #     'hotkeys': ['right'],
    # },
    'windows+up': {
        'target': {'pname': 'AIMP.exe', 'title': 'TrayControl'},
        'hotkeys': ['up'],
    },
    'windows+down': {
        'target': {'pname': 'AIMP.exe', 'title': 'TrayControl'},
        'hotkeys': ['down'],
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
        'hotkeys': ['up', 'ctrl+j', '6', '0', 'enter'],
    },
    'ctrl+windows+down': {
        'interval': 0.2,
        # 'target': {'pname': 'AIMP.exe', 'title': 'TrayControl'},
        'hotkeys': ['down', 'ctrl+j', '6', '0', 'enter'],
    },
    # 'ctrl+windows+left': {
    #     'interval': 0.2,
    #     'hotkeys': ['ctrl+windows+left'], 60
    # }, 60
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

MIDIKEY_PRESET = {
    'note+41': {
        'hotkeys': ['ctrl+alt+shift+f1']
    },
    'note+43': {
        'hotkeys': ['ctrl+alt+shift+f2']
    },
    'note+45': {
        'hotkeys': ['ctrl+alt+shift+f3']
    },
    'note+47': {
        'hotkeys': ['ctrl+alt+shift+f4']
    },
    'note+72': {
        'hotkeys': ['ctrl+alt+shift+f12']
    }
}


class RepeatHandler():

    def __init__(self, hotkeys):
        self.hotkeys = hotkeys
        self.timestamp = time.time()


class MidiToKey():

    def __init__(self, parent=None):
        self.repeats = []
        self.parent = parent
        self.stopsignal = False

    def repeat_timer(self):
        while not self.stopsignal:
            time.sleep(0.001)
            timestamp = time.time()
            for repeat in self.repeats:
                if timestamp < repeat.timestamp + 0.5:
                    continue
                # pyautogui.hotkey(*repeat.hotkey)
                self.handle_hotkeys(repeat.hotkeys)

    def insert_repeat(self, hotkeys):
        self.repeats += [RepeatHandler(hotkeys)]

    def remove_repeat(self, hotkeys):
        for i in range(len(self.repeats) - 1, -1, -1):
            if self.repeats[i].hotkeys == hotkeys:
                self.repeats.pop(i)

    def handle_hotkeys(self, hotkeys):
        for hotkey in hotkeys:
            if isinstance(hotkey, str):
                keyboard.send(hotkey, do_press=True, do_release=True)
            if isinstance(hotkey, int) or isinstance(hotkey, float):
                time.sleep(hotkey)

    def handle_notes(self, message, notes, hotkeys):
        if message.note in notes:
            if message.type == 'note_on':
                # pyautogui.hotkey(*hotkey)
                self.handle_hotkeys(hotkeys)
                self.insert_repeat(hotkeys)
            if message.type == 'note_off':
                self.remove_repeat(hotkeys)

    def midi_frame(self, message):
        if message.type == 'aftertouch':
            return
        print(message)
        if message.type.startswith('note'):
            preset = MIDIKEY_PRESET.get('+'.join(['note', str(message.note)]))
            if preset:
                self.handle_notes(message, (message.note,), preset['hotkeys'])

    def midi_watcher(self):
        with mido.open_input() as inport:
            for message in inport:
                if self.stopsignal:
                    return
                self.midi_frame(message)

    def run(self):
        self.repeat_timer_thread = threading.Thread(target=self.repeat_timer)
        self.repeat_timer_thread.daemon = True
        self.repeat_timer_thread.start()

        self.midi_watcher_thread = threading.Thread(target=self.midi_watcher)
        self.midi_watcher_thread.daemon = True
        self.midi_watcher_thread.start()

    def stop(self):
        self.stopsignal = True


class HotKeyManager(wx.Timer):

    def __init__(self, parent):
        wx.Timer.__init__(self)
        self.windows = []
        self.parent = parent
        self.stopsignal = False
        self.interval = 100
        self.parent = parent
        # self.miditokey = MidiToKey(self)
        # self.miditokey.run()
        self.bind_keyboard()
        self.Start(self.interval)

    def Notify(self):
        # print('xxx')
        pass

    def get_foreground_window(self):
        hwnd = win32gui.GetForegroundWindow()
        for window in self.windows:
            if window.hwnd == hwnd:
                return window
        for i in range(10):
            window = ForegroundWindowHandler()
            if not window.error:
                self.windows += [window]
                return window
                break
            time.sleep(0.05)

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
            if not hasattr(self, 'target'):
                self.target = uiautomation.WindowControl(searchDepth=1, ClassName='TAIMPMainForm')
            # print(xxx.Handle)
            # self.target.SetTopmost(True)
            origin = self.get_foreground_window()
            # target = self.get_target_window(**preset['target'])
            if not origin or not self.target:
                return
            # print(target.pname, target.title)
            # try:
            #     win32gui.SetForegroundWindow(target.hwnd)
            # except Exception:
            #     print('handle_hotkey(): focusing target failed', target.hwnd)
            #     return
            # time.sleep(0.01)
        print(preset['hotkeys'])
        # keyboard.send('windows', do_press=True, do_release=True)

        for hk in preset['hotkeys']:
            # self.target.SendKeys('{Right}')
            if isinstance(hk, str):
                # keys = hk.split('+')
                # keys = ''.join(['{%s}' % (v.capitalize()) for v in keys if v])
                # print(keys)
                # self.target.SendKeys(keys, interval=0, waitTime=0)
                keyboard.send(hk, do_press=True, do_release=True)
            if isinstance(hk, int) or isinstance(hk, float):
                time.sleep(hk)

        if 'target' in preset:
            try:
                win32gui.SetForegroundWindow(origin.hwnd)
            except Exception:
                print('handle_hotkey(): focusing origin failed', origin.hwnd)
                # print(origin.hwnd, origin.pname, origin.title, origin.pid)

    def keyboard_hook_callback(self, event):
        # print(event.name)

        class EventLog():

            def __init__(self, name):
                self.name = name
                self.time = time.time()

        modifiers = sorted(['alt', 'ctrl', 'shift', 'windows'])
        mods = [v for v in modifiers if keyboard.is_pressed(v)]
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
            keypad = ''
            hotkey = mods + '+%s' % (keypad + event.name)
            if LAYOUT_PRESET.get(hotkey):
                self.handle_layout(hotkey)
            # if HOTKEY_PRESET.get(hotkey):
            #     self.handle_hotkey(hotkey)

    def suppressed_hotkey_callback(self, hotkey, event):

        # print(hotkey.ljust(14), int(keyboard.is_pressed(hotkey)), int(
        #     event.is_keypad), str(event.time).split('.')[-1][-4:])
        # print('-' * 60)

        if LAYOUT_PRESET.get(hotkey):
            self.handle_layout(hotkey)
        # if HOTKEY_PRESET.get(hotkey):
        #     self.handle_hotkey(hotkey)

    def stop(self, event=None):
        # self.thread.stop()
        self.unbind_keyboard()
        # self.miditokey.stop()
        self.stopsignal = True

    def unbind_keyboard(self):
        keyboard.unhook_all()
        self.keyboard_binded = False
        print('unbind_keyboard(): keyboard_unbinded')

    def bind_keyboard(self):
        keyboard.unhook_all()
        # keyboard.hook(self.keyboard_hook_callback)
        presets = list(LAYOUT_PRESET.keys())
        # presets += list(HOTKEY_PRESET.keys())
        for hotkey in [v.replace('keypad', '') for v in presets]:
            keyboard.add_hotkey(hotkey, self.suppressed_hotkey_callback, args=(hotkey,),
                                suppress=True, timeout=1, trigger_on_release=False)
        self.keyboard_binded = True
        print('bind_keyboard(): keyboard_binded')


class ScreenLockWatcher(wx.Timer):

    def __init__(self, parent):
        wx.Timer.__init__(self)
        self.parent = parent
        self.interval = 100
        self.screen_locked = self.is_screen_locked()
        self.Start(self.interval)

    def Notify(self):
        screen_locked = self.is_screen_locked()
        if not self.screen_locked and screen_locked:
            print('------[  SCREEN LOCKED  ]------')
            self.screen_locked = True
            # self.hotkey_manager.stop()
            self.parent.hotkey_manager.unbind_keyboard()
        elif self.screen_locked and not screen_locked:
            self.screen_locked = False

            # self.parent.hotkey_manager.stop()
            self.parent.hotkey_manager.unbind_keyboard()
            self.parent.hotkey_manager.bind_keyboard()
            # python = 'pythonw.exe' if __file__.endswith('.pyw') else 'python.exe'
            # command = '%s %s %d' % (python, __file__, self.pid)
            # command = '%s %s' % (python, __file__)
            # proc = subprocess.Popen(command, shell=True)
            # proc.communicate()
            # self.parent.on_exit()
            print('------[ SCREEN UNLOCKED ]------')
            # self.visible = False
            # self._update_icon()
            # python = 'pythonw.exe' if __file__.endswith('.pyw') else 'python.exe'
            # # command = '%s %s %d' % (python, __file__, self.pid)
            # command = '%s %s' % (python, __file__)
            # proc = subprocess.Popen(command, shell=True)
            # proc.communicate()
            # os.kill(self.pid, signal.SIGTERM)

    def is_screen_locked(self):
        if not hasattr(self, '__screen_locked_log__'):
            self.__screen_locked_log__ = []

        class ScreenLockedLog():

            def __init__(self):
                self.time = time.time()
                hwnd = win32gui.GetForegroundWindow()
                self.value = hwnd == 0
                if hwnd != 0:
                    window = WindowInformation(hwnd)
                    self.value = not window.pname and window.title == '작업 관리자'

        self.__screen_locked_log__ += [ScreenLockedLog()]
        self.__screen_locked_log__ = self.__screen_locked_log__[-100:]
        logs = self.__screen_locked_log__[-3:]
        return len(logs) == len([v.value for v in logs if v.value])


class RemoteDesktopWatcher(wx.Timer):

    def __init__(self, parent):
        wx.Timer.__init__(self)
        self.parent = parent
        self.interval = 50
        # self.screen_locked_state = self.is_screen_locked()
        self.desktop_remoted = self.is_desktop_remoted()
        self.Start(self.interval)

    def Notify(self):
        # self.desktop_remoted = self.is_screen_locked() or self.is_desktop_remoted()
        # while not self.stopsignal:
        if not self.desktop_remoted and self.is_desktop_remoted():
            print('------[  DESKTOP REMOTED  ]------')
            self.desktop_remoted = True
            self.parent.hotkey_manager.unbind_keyboard()
        elif self.desktop_remoted and not self.is_desktop_remoted():
            self.desktop_remoted = False
            self.parent.hotkey_manager.bind_keyboard()
            print('------[ DESKTOP UNREMOTED ]------')

    def is_desktop_remoted(self):
        window = ForegroundWindowHandler()
        return window and window.pname == 'mstsc.exe'
