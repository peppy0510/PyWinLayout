# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import os

from base import create_desktop_ini
from base import create_shortcut
from base import run_as_admin


def main():
    # C:\Users\username\AppData\Roaming\Microsoft\Windows\Start Menu
    # C:\Users\username\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
    shortcut_name = 'hotkey.py'
    target_name = 'hotkey.py'
    cwd = os.path.dirname(__file__)
    home = os.path.expanduser('~')
    icon = os.path.join(cwd, 'assets', 'icon.ico')
    startmenu = os.path.join(home, 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu')
    startup = os.path.join(startmenu, 'Programs', 'Startup')
    python = 'pythonw.exe'
    create_shortcut(
        os.path.join(startmenu, shortcut_name),
        python, os.path.join(cwd, target_name), cwd, icon)

    create_shortcut(
        os.path.join(startup, shortcut_name),
        python, os.path.join(cwd, target_name), cwd, icon)

    create_desktop_ini(cwd, icon)


if __name__ == '__main__':
    main()
    # run_as_admin(main, __file__)
