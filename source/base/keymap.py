# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import win32con


# https://github.com/nvaccess/nvda-misc-deps/blob/master/python/win32con.py


KEYMAP = {
    '0': 0x30,
    '1': 0x31,
    '2': 0x32,
    '3': 0x33,
    '4': 0x34,
    '5': 0x35,
    '6': 0x36,
    '7': 0x37,
    '8': 0x38,
    '9': 0x39,
    'A': 0x41,
    'B': 0x42,
    'C': 0x43,
    'D': 0x44,
    'E': 0x45,
    'F': 0x46,
    'G': 0x47,
    'H': 0x48,
    'I': 0x49,
    'J': 0x4A,
    'K': 0x4B,
    'L': 0x4C,
    'M': 0x4D,
    'N': 0x4E,
    'O': 0x4F,
    'P': 0x50,
    'Q': 0x51,
    'R': 0x52,
    'S': 0x53,
    'T': 0x54,
    'U': 0x55,
    'V': 0x56,
    'W': 0x57,
    'X': 0x58,
    'Y': 0x59,
    'Z': 0x5A,
    '*': 0x6A,
    '+': 0x6B,
    '|': 0x6C,
    '-': 0x6D,
    '/': 0x6F,
    '.': 0x6E,
    'space': 0x20,
    'esc': 0x1B,
    'num0': 0x60,
    'num1': 0x61,
    'num2': 0x62,
    'num3': 0x63,
    'num4': 0x64,
    'num5': 0x65,
    'num6': 0x66,
    'num7': 0x67,
    'num8': 0x68,
    'num9': 0x69,
    'win': win32con.MOD_WIN,
    'alt': win32con.MOD_ALT,
    'ctrl': win32con.MOD_CONTROL,
    'shift': win32con.MOD_SHIFT,
}
