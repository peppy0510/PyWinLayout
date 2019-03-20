# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import ScriptingBridge


def main():
    app = ScriptingBridge.SBApplication.applicationWithBundleIdentifier_('com.apple.Finder')
    window = app.windows()[0]
    print(dir(window))
    window.setBounds_([[1440, 2560 / 2], [1440, 2560 / 2]])
    window.setPosition_([-1440, 0])


if __name__ == '__main__':
    main()
