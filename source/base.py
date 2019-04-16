# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import ctypes
import operator
import os
import psutil
import screeninfo
import sys
import time
import win32api
import win32con
import win32gui
import win32process
import winreg

from win32com.client import Dispatch


CMD = r'C:\\Windows\\System32\\cmd.exe'
FOD_HELPER = r'C:\\Windows\\System32\\fodhelper.exe'
PYTHON_CMD = 'python'
REG_PATH = r'Software\Classes\ms-settings\shell\open\command'
DELEGATE_EXEC_REG_KEY = 'DelegateExecute'


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def create_reg_key(key, value):
    '''
    Creates a reg key
    '''
    try:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, key, 0, winreg.REG_SZ, value)
        winreg.CloseKey(registry_key)
    except WindowsError:
        raise


def bypass_uac(cmd):
    '''
    Tries to bypass the UAC
    '''
    try:
        create_reg_key(DELEGATE_EXEC_REG_KEY, '')
        create_reg_key(None, cmd)
    except WindowsError:
        raise


def run_as_admin(callback, file, try_run_as_admin=True):
    if try_run_as_admin is False or is_admin():
        callback()
    else:
        print(sys.executable)
        create_reg_key(DELEGATE_EXEC_REG_KEY, '')

        # cwd = os.path.dirname(os.path.realpath(file))
        # command = '{} /k {} {}'.format(sys.executable, file, cwd)
        # command = '{} /k {}'.format(sys.executable, file)
        # create_reg_key(None, command)
        # create_reg_key(None, cmd)
        # Rerun with admin rights
        # try:
        #     current_dir = os.path.dirname(os.path.realpath(__file__)) + '\\' + __file__
        #     cmd = '{} /k {} {}'.format(CMD, PYTHON_CMD, current_dir)
        #     bypass_uac(cmd)
        #     os.system(FOD_HELPER)
        #     sys.exit(0)
        # except WindowsError:
        #     sys.exit(1)

        ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, file, None, 1)


def get_self_process_name():
    pid = int(os.getpid())
    for p in psutil.process_iter():
        try:
            p.name()
        except Exception:
            pass
        if p.pid == pid:
            return p.name()


def kill_existing_instances():
    pid = int(os.getpid())
    pname = get_self_process_name()
    cwd = os.path.split(__file__)[0]
    for p in psutil.process_iter():
        try:
            p.cwd()
            p.name()
        except Exception:
            continue
        if p.pid == pid:
            continue
        if p.cwd() == cwd and p.name().lower() in ('python.exe', 'pythonw.exe',):
            # only SIGTERM, CTRL_C_EVENT, CTRL_BREAK_EVENT signals on Windows Platform.
            # p.send_signal(signal.SIGTERM)
            p.terminate()
        if pname.endswith('.exe') and pname == p.name():
            p.terminate()


def create_shortcut(path, target_path='', arguments='', working_directory='', icon=''):
    ext = os.path.splitext(path)[-1][1:].lower()
    if ext == 'url':
        with open(path, 'w') as file:
            file.write('[InternetShortcut]\nURL=%s' % target_path)
    else:
        shell = Dispatch('WScript.Shell')

        shortcut = shell.CreateShortCut(
            path if path.endswith('.lnk') else '.'.join([path, 'lnk']))
        # shortcut.WindowStyle = 1
        shortcut.Arguments = arguments
        shortcut.Targetpath = target_path
        shortcut.WorkingDirectory = working_directory
        if icon:
            shortcut.IconLocation = icon
        shortcut.save()
    print('[ SHORTCUT CREATED ] [ %s ]' % path)


def create_desktop_ini(directory, icon_resource, folder_type='Generic'):
    with open(os.path.join(directory, 'desktop.ini'), 'w') as file:
        file.write('\n'.join([
            '[.ShellClassInfo]', 'IconResource=%s,0' % icon_resource,
            '[ViewState]', 'Mode=', 'Vid=', 'FolderType=%s' % folder_type]))


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


class ScreenShown():

    def __init__(self, offset_x, offset_y, finish_x, finish_y):
        self.offset = Coordination(offset_x, offset_y)
        self.finish = Coordination(finish_x, finish_y)
        self.width = self.finish.x - self.offset.x
        self.height = self.finish.y - self.offset.y
        direction = -1 if self.width < 0 or self.height < 0 else 1
        self.size = abs(self.width * self.height) * direction


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

    def get_screens(self):
        screens = sorted([Rectangle(v.x, v.y, v.x + v.width, v.y + v.height)
                          for v in screeninfo.get_monitors()], key=operator.attrgetter('offset.x'))

        for screen in screens:
            monitor_info = win32api.GetMonitorInfo(
                win32api.MonitorFromPoint((screen.offset.x, screen.offset.y)))

            monx, mony, monw, monh = monitor_info.get('Monitor')
            workx, worky, workw, workh = monitor_info.get('Work')

            if monw == workw and worky != mony:  # taskbar top
                screen.offset.y += worky - mony
            if monw == workw and worky == mony:  # taskbar bottom
                screen.finish.y -= monh - workh
            if monh == workh and workx != monx:  # taskbar left
                screen.offset.x += workx - monx
            if monh == workh and workx == monx:  # taskbar right
                screen.finish.x -= monw - workw

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