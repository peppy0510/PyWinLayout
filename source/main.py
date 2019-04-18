# encoding: utf-8


__appname__ = 'PyWinLayout'
__version__ = '0.1.1'
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
from base import get_current_real_cwq
from base import get_screens
from base import kill_existing_instances
from base import run_as_admin  # noqa
from presets import LAYOUT_PRESETS


class AboutDialog(wx.Dialog):

    def __init__(self, parent, style=0):
        self.parent = parent

        style = style | wx.CLIP_CHILDREN |\
            wx.NO_FULL_REPAINT_ON_RESIZE | wx.STAY_ON_TOP | wx.NO_BORDER

        wx.Dialog.__init__(self, parent, id=-1, title='', size=(300, 250), style=style)

        self.SetIcon(wx.Icon(self.parent.taskbar.icon_path))

        self.SetTransparent(220)
        self.SetBackgroundColour((0, 0, 0))

        width, height = self.GetClientSize()
        screen = get_screens()[0]
        self.SetPosition((
            int((screen.width - width) * 0.5),
            int((screen.height - height) * 0.5),
        ))

        icon_size = 48
        image = wx.Image(self.parent.taskbar.icon_path, wx.BITMAP_TYPE_ANY)
        image = image.Scale(icon_size, icon_size, wx.IMAGE_QUALITY_HIGH)
        image = wx.Bitmap(image)
        image = wx.StaticBitmap(self, -1, image)
        image.SetPosition((int((width - icon_size) * 0.5), 25))

        button = wx.Button(self, -1, 'Close', style=wx.BORDER_NONE)
        button.SetSize((100, 26))
        button.SetPosition((int((width - 100) * 0.5), height - 26 - 30))
        button.SetBackgroundColour((200, 200, 200))
        button.Bind(wx.EVT_BUTTON, self.OnClose)

        def create_static_text(label, offsetY):
            font = wx.Font(10, wx.SWISS, wx.NORMAL,
                           wx.FONTWEIGHT_BOLD, faceName='Consolas')
            text = wx.StaticText(self, label=label)
            text.SetFont(font)
            text.SetForegroundColour((220, 220, 220))
            w, h = text.GetClientSize()
            text.SetPosition((int((width - w) * 0.5), offsetY))
            return text

        offsetY = 92
        create_static_text('{}'.format(__appname__), offsetY)
        offsetY += 20
        create_static_text('Version: {}'.format(__version__), offsetY)
        offsetY += 20
        create_static_text('Author: {}'.format(__author__), offsetY)
        offsetY += 20
        create_static_text('Email: {}'.format(__email__), offsetY)

    def OnClose(self, event):
        self.EndModal(True)


class TaskBarIcon(wx.adv.TaskBarIcon):

    tray_tooltip = '{} {}'.format(__appname__, __version__,)
    tray_icon_path = os.path.join('assets', 'icon', 'icon.ico')

    def __init__(self, parent):
        super(TaskBarIcon, self).__init__()
        self.parent = parent
        cwd = os.path.dirname(get_current_real_cwq())
        self.icon_path = os.path.join(cwd, self.tray_icon_path)
        if hasattr(sys, '_MEIPASS'):
            self.icon_path = os.path.join(sys._MEIPASS, self.tray_icon_path)
        self.set_icon(self.icon_path)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.OnClickTrayIcon)

    def OnClickTrayIcon(self, event):
        self.PopupMenu(self.CreatePopupMenu())

    def OnClickAboutMenu(self, event):
        dialog = AboutDialog(self.parent)
        dialog.ShowModal()
        dialog.Destroy()

    def CreatePopupMenu(self):
        self.menu = wx.Menu()
        # self.menu.SetTitle('{} {}'.format(__appname__, __version__,))
        self.create_menu_item('About {}'.format(
            __appname__), self.OnClickAboutMenu)
        self.menu.AppendSeparator()

        self.run_on_startup = self.create_menu_item(
            'Run on Startup', self.OnToggleRunOnStartup, kind=wx.ITEM_CHECK)
        if ShortCut.has_user_startup(__appname__):
            self.run_on_startup.Check(True)

        self.menu.AppendSeparator()
        self.create_menu_item('Quit', self.parent.OnClose)

        return self.menu

    def create_menu_item(self, label, callback=None, **kwargs):
        item = wx.MenuItem(self.menu, -1, label, **kwargs)
        self.menu.Bind(wx.EVT_MENU, callback, id=item.GetId())
        self.menu.Append(item)
        return item

    def set_icon(self, path):
        if path.lower().endswith('.ico'):
            icon = wx.Icon(path)
        else:
            icon = wx.Icon(wx.Bitmap(path))
        self.SetIcon(icon, self.tray_tooltip)

    def show_balloon(self, message, displaytime=2 * 1000):
        title = __appname__
        self.ShowBalloon(title, message, displaytime)

    def OnToggleRunOnStartup(self, event):
        path = ShortCut.get_user_startup_path(__appname__)
        if os.path.exists(path):
            os.remove(path)
            self.show_balloon('Run on startup has been disabled.')
        else:
            if hasattr(sys, '_MEIPASS'):
                working_directory = 'C:\\Program Files\\{}'.format(__appname__)
                if not os.path.exists(working_directory):
                    working_directory = 'C:\\Program Files (x86)\\{}'.format(__appname__)
                target_path = os.path.join(working_directory, '{}.exe'.format(__appname__))
                arguments = ''
                icon = ''
            else:
                working_directory = os.path.dirname(get_current_real_cwq())
                target_path = 'pythonw.exe'
                arguments = '"{}"'.format(os.path.join(
                    working_directory, 'source', os.path.basename(__file__)))
                icon = os.path.join(working_directory, self.tray_icon_path)

            ShortCut.create(
                path=path,
                target_path=target_path,
                arguments=arguments,
                working_directory=working_directory,
                icon=icon)

            self.show_balloon('Run on startup has been enabled.')


class MainFrame(wx.Frame):

    def __init__(self, parent=None):

        wx.Frame.__init__(self, parent, id=wx.ID_ANY, size=wx.Size(0, 0))

        self.taskbar = TaskBarIcon(self)
        self.window_layout_manager = WindowLayoutManager()
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

    def OnClose(self, event=None):
        self.unbind_hotkey()
        # self.other_instance_watcher.Stop()
        wx.CallAfter(self.taskbar.Destroy)
        wx.CallAfter(self.Destroy)
        # print('OnClose')


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
