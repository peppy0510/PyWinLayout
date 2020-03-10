# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import operator
import os
import time
import win32api
import win32con
import win32gui
import win32process

from .coordination import Coordination
from .rectangle import Rectangle
from .screens import ScreenShown
from .screens import get_screens


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


class WindowLayoutHandler(WindowInformation, Rectangle):

    def __init__(self):
        self.error = False
        for i in range(10):
            hwnd = win32gui.GetForegroundWindow()
            super(self.__class__, self).__init__(hwnd)
            if self.error:
                return
        self.layout_index = 0
        self.refresh()

    def refresh(self):
        self.screens = get_screens()
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

            screen.shown = ScreenShown(offset_x, offset_y, finish_x, finish_y)

        self.screen = sorted(self.screens, key=operator.attrgetter('shown.size'))[-1]

    def get_next_rect(self):
        preset = self.preset[self.screen.orientation]
        index = self.layout_index + 1
        index = 0 if index > len(preset) - 1 else index
        self.layout_index = index
        xp, yp, wp, hp = preset[index]
        x = self.screen.offset.x + self.screen.width * xp
        y = self.screen.offset.y + self.screen.height * yp
        width = self.screen.width * wp
        height = self.screen.height * hp
        return int(round(x)), int(round(y)), int(round(width)), int(round(height))

    def resize(self, preset):
        self.preset = preset
        self.refresh()
        x, y, width, height = self.get_next_rect()
        if not self.__resize__(x, y, width, height):
            return

        rect = win32gui.GetWindowRect(self.hwnd)
        delta_x = rect[2] - self.screen.finish.x
        delta_y = rect[3] - self.screen.finish.y

        # right align if window has minimum width and overflow
        if delta_x > 0:
            x -= delta_x
            width += delta_x
            if not self.__resize__(x, y, width, height):
                return

        rect = win32gui.GetWindowRect(self.hwnd)
        delta_x = rect[2] - self.screen.finish.x
        delta_y = rect[3] - self.screen.finish.y
        # bottom align if window has minimum height and overflow
        if delta_y > 0:
            y -= delta_y
            height += delta_y
            if not self.__resize__(x, y, width, height):
                return

    def __resize__(self, x, y, width, height, repaint=True):
        try:
            win32gui.ShowWindow(self.hwnd, win32con.SW_NORMAL)
            win32gui.MoveWindow(self.hwnd, x, y, width, height, repaint)
            return True
        except Exception:
            print('Admin rights required.')
        return False


class WindowLayoutManager():

    def resize_foreground_window(self, preset):
        window = self.get_foreground_window()
        if window:
            window.resize(preset)

    def get_foreground_window(self):
        if not hasattr(self, '__proxy_window_layout_handlers__'):
            self.__proxy_window_layout_handlers__ = []

        hwnd = win32gui.GetForegroundWindow()
        for window in self.__proxy_window_layout_handlers__:
            if window.hwnd == hwnd:
                return window

        for i in range(10):
            window = WindowLayoutHandler()
            if not window.error:
                self.__proxy_window_layout_handlers__ += [window]
                return window
            time.sleep(0.05)
