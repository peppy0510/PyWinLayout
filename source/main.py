# encoding: utf-8


__appname__ = 'PyWinLayout'
__version__ = '0.0.3'
__author__ = 'Taehong Kim'
__email__ = 'peppy0510@hotmail.com'
__license__ = ''
__doc__ = '''
'''


import os
import sys
import wx
import wx.adv

from base import ShortCut
from base import WindowLayoutManager
from base import kill_existing_instances
from base import run_as_admin
from presets import LAYOUT_PRESETS


class TaskBarIcon(wx.adv.TaskBarIcon):

    tray_tooltip = '{} {}'.format(__appname__, __version__,)
    tray_icon_path = os.path.join('assets', 'icon', 'icon.ico')
    if not os.path.exists(tray_icon_path):
        tray_icon_path = os.path.join('..', tray_icon_path)

    def __init__(self, parent):
        super(TaskBarIcon, self).__init__()
        self.parent = parent
        # startmenu = os.path.join(os.path.expanduser('~'), 'AppData',
        #                          'Roaming', 'Microsoft', 'Windows', 'Start Menu')
        # startup = os.path.join(startmenu, 'Programs', 'Startup')
        # self.run_on_startup_path = os.path.join(startup, __appname__)

        self.set_icon(self.tray_icon_path)

    def CreatePopupMenu(self):
        self.menu = wx.Menu()
        self.menu.SetTitle('{} {}'.format(__appname__, __version__,))
        self.run_on_startup = self.create_menu_item(
            'Run on Startup', self.parent.OnToggleRunOnStartup)
        self.menu.AppendSeparator()
        self.create_menu_item('Author: {}'.format(__author__))
        self.create_menu_item('Email: {}'.format(__email__))
        self.menu.AppendSeparator()
        self.create_menu_item('Quit {}'.format(__appname__), self.parent.OnClose)

        if ShortCut.has_user_startup(__appname__):
            self.run_on_startup.Check(True)

        return self.menu

    def create_menu_item(self, label, func=None):
        item = wx.MenuItem(self.menu, -1, label, kind=wx.ITEM_CHECK)
        self.menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        self.menu.Append(item)
        return item

    def set_icon(self, path):
        if path.lower().endswith('.ico'):
            icon = wx.Icon(path)
        else:
            icon = wx.Icon(wx.Bitmap(path))
        self.SetIcon(icon, self.tray_tooltip)


class MainFrame(wx.Frame):

    def __init__(self, parent=None):

        wx.Frame.__init__(self, parent, id=wx.ID_ANY, size=wx.Size(0, 0))

        self.taskbar = TaskBarIcon(self)
        self.window_layout_manager = WindowLayoutManager()
        # self.other_instance_watcher = OtherInstanceWatcher(self)
        # self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.bind_hotkey()

    def bind_hotkey(self):
        for preset in LAYOUT_PRESETS:
            self.RegisterHotKey(preset['event_id'], *preset['codes'])
            self.Bind(wx.EVT_HOTKEY, self.handle_hotkey, id=preset['event_id'])

    def unbind_hotkey(self):
        for preset in LAYOUT_PRESETS:
            self.Unbind(wx.EVT_HOTKEY, id=preset['event_id'])
            self.UnregisterHotKey(preset['event_id'])

    def handle_hotkey(self, event):
        for preset in LAYOUT_PRESETS:
            if preset['event_id'] == event.GetId():
                self.window_layout_manager.resize_foreground_window(preset)

    def OnToggleRunOnStartup(self, event):
        path = ShortCut.get_user_startup_path(__appname__)
        if os.path.exists(path):
            os.remove(path)
        else:
            if hasattr(sys, '_MEIPASS'):
                working_directory = 'C:\\Program Files\\{}'.format(__appname__)
                if not os.path.exists(working_directory):
                    working_directory = 'C:\\Program Files (x86)\\{}'.format(__appname__)
                target_path = os.path.join(working_directory, '{}.exe'.format(__appname__))
                arguments = ''
                icon = ''
            else:
                working_directory = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
                target_path = 'pythonw.exe'
                arguments = '"{}"'.format(os.path.join(
                    working_directory, 'source', os.path.basename(__file__)))
                icon = os.path.join(working_directory, self.taskbar.tray_icon_path.strip('.\\'))

            ShortCut.create(
                path=path,
                target_path=target_path,
                arguments=arguments,
                working_directory=working_directory,
                icon=icon)

    def OnClose(self, event=None):
        self.unbind_hotkey()
        # self.other_instance_watcher.Stop()
        wx.CallAfter(self.taskbar.Destroy)
        wx.CallAfter(self.Destroy)
        print('OnClose')


class HotKeyApp(wx.App):

    def __init__(self, parent=None, *argv, **kwargs):
        wx.App.__init__(self, parent, *argv, **kwargs)

    def FilterEvent(self, event):
        return -1

    def OnPreInit(self):
        self.MainFrame = MainFrame()

    def OnClose(self, event=None):
        pass

    def __del__(self):
        pass


def main():
    app = HotKeyApp()
    app.MainLoop()


if __name__ == '__main__':
    kill_existing_instances()
    main()
    # run_as_admin(main, __file__)
