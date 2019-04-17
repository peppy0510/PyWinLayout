# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import operator
import screeninfo
import win32api

from .coordination import Coordination
from .rectangle import Rectangle


class ScreenShown():

    def __init__(self, offset_x, offset_y, finish_x, finish_y):
        self.offset = Coordination(offset_x, offset_y)
        self.finish = Coordination(finish_x, finish_y)
        self.width = self.finish.x - self.offset.x
        self.height = self.finish.y - self.offset.y
        direction = -1 if self.width < 0 or self.height < 0 else 1
        self.size = abs(self.width * self.height) * direction


def get_screens():
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
