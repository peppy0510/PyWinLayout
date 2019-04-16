# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import hashlib

from keymap import KEYMAP


LAYOUT_PRESETS = [
    {
        'hotkey': 'win+num5',
        'landscape': [((1 - v) / 2, 0.00, v, 1.00) for v in (1.00, 0.50, 0.34,)],
        'portrait': [(0.00, (1 - v) / 2, 1.00, v) for v in (1.00, 0.50,)]
    }, {
        'hotkey': 'win+num2',
        'landscape': [((1 - v) / 2, 0.50, v, 0.50) for v in (1.00, 0.50, 0.34,)],
        'portrait': [(0.00, 1 - v, 1.00, v) for v in (0.75, 0.50, 0.25,)]
    }, {
        'hotkey': 'win+num8',
        'landscape': [((1 - v) / 2, 0.00, v, 0.50) for v in (1.00, 0.50, 0.34,)],
        'portrait': [(0.00, 0.00, 1.00, v) for v in (0.75, 0.50, 0.25,)]
    }, {
        'hotkey': 'win+num4',
        'landscape': [(0.00, 0.00, v, 1.00) for v in (0.67, 0.50, 0.33,)],
        'portrait': [(0.00, (1 - v) / 2, 0.50, v) for v in (1.00, 0.50,)]
    }, {
        'hotkey': 'win+num6',
        'landscape': [(1 - v, 0.00, v, 1.00) for v in (0.67, 0.50, 0.33,)],
        'portrait': [(0.50, (1 - v) / 2, 0.50, v) for v in (1.00, 0.50,)]
    }, {
        'hotkey': 'win+num1',
        'landscape': [(0.00, 0.50, v, 0.50) for v in (0.67, 0.50, 0.33,)],
        'portrait': [(0.00, 1 - v, 0.50, v) for v in (0.75, 0.50, 0.25,)]
    }, {
        'hotkey': 'win+num3',
        'landscape': [(1 - v, 0.50, v, 0.50) for v in (0.67, 0.50, 0.33,)],
        'portrait': [(0.50, 1 - v, 0.50, v) for v in (0.75, 0.50, 0.25,)]
    }, {
        'hotkey': 'win+num7',
        'landscape': [(0.00, 0.00, v, 0.50) for v in (0.67, 0.50, 0.33,)],
        'portrait': [(0.00, 0.00, 0.50, v) for v in (0.75, 0.50, 0.25,)]
    }, {
        'hotkey': 'win+num9',
        'landscape': [(1 - v, 0.00, v, 0.50) for v in (0.67, 0.50, 0.33,)],
        'portrait': [(0.50, 0.00, 0.50, v) for v in (0.75, 0.50, 0.25,)]
    },
]


def operate_or(values):
    value = values[0]
    for v in values[1:]:
        value = value | v
    return value


def organize_presets(presets):
    modifiers = sorted(['alt', 'ctrl', 'shift', 'windows'])
    for i in range(len(presets) - 1, -1, -1):
        keys = presets[i]['hotkey'].split('+')
        mods = [v for v in modifiers if v in keys]
        base = [v for v in keys if v and v not in modifiers]
        presets[i]['hotkey'] = '+'.join(mods + base)

        keys = presets[i]['hotkey'].split('+')
        codes = [KEYMAP.get(key) for key in keys]
        if None in codes:
            presets.pop(i)
            continue

        codes = [v for v in codes if v is not None]

        presets[i]['codes'] = (operate_or(codes[:-1]), codes[-1],)
        m = hashlib.new('md5')
        m.update(''.join([str(v) for v in presets[i]['codes']]).encode('utf-8'))
        presets[i]['event_id'] = int(m.hexdigest()[:5], 16)

    return presets


LAYOUT_PRESETS = organize_presets(LAYOUT_PRESETS)


def test():
    for preset in LAYOUT_PRESETS:
        print(preset)


if __name__ == '__main__':
    test()
