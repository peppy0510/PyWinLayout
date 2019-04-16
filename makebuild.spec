# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import glob
import os
import re


debug = False
upx = True
onefile = True


PYZ = PYZ  # noqa
EXE = EXE  # noqa
COLLECT = COLLECT  # noqa
Analysis = Analysis  # noqa


def get_appname():
    ptrn = (r'''[_]{0,2}appname[_]{0,2}[\s]{1,}[=]{1}[\s]{1,}'''
            r'''['"]{1}([a-zA-Z\s]{1,})['"]{1}''')
    with open(os.path.join('source', 'main.py'), 'r') as file:
        content = file.read()
        m = re.search(ptrn, content)
        if m:
            return m.group(1)


appname = get_appname()


class Path():

    def __init__(self, **kwargs):
        for key in kwargs.keys():
            kwargs[key] = os.path.abspath(kwargs[key])
        self.__dict__.update(kwargs)


def grapdatas(home, path, depth, mode, specs=None):
    datas = []
    for p in glob.glob(os.path.join(home, path, '*.*')):
        splpath = p.split(os.sep)
        if specs is None or splpath[-1] in specs:
            virpath = os.sep.join(splpath[-depth - 1:])
            datas += [(virpath, p, mode)]
    return datas

# runtime_tmpdir = '%HOMEPATH%\\AppData\\Local\\Temp\\' + name


path = Path(
    home='',
    assets='assets',
    icon=os.path.join('assets', 'icon', 'icon.ico'),
    dlls=os.path.join('assets', 'dlls'),
    output=os.path.join('build', '{}.exe'.format(appname)),
    winsxs86=('C:\\Windows\\WinSxS\\x86_microsoft-windows-m..'
              'namespace-downlevel_31bf3856ad364e35_10.0.17763.1_none_5c0c291220e648a1'),
    winsxs64=('C:\\Windows\\WinSxS\\amd64_microsoft-windows-m..'
              'namespace-downlevel_31bf3856ad364e35_10.0.17763.1_none_b82ac495d943b9d7')
)

a = Analysis([os.path.join('source', 'main.py')],
             hookspath=[path.home, path.assets],
             pathex=[path.home, path.assets, path.dlls, path.winsxs64],
             hiddenimports=[])

a.datas += grapdatas(path.home, 'assets', 1, 'data', ['icon.ico'])

pyz = PYZ(a.pure)

if onefile:
    exe = EXE(pyz, a.scripts + [('O', '', 'OPTION')],
              a.binaries, a.zipfiles, a.datas,
              uac_admin=True, uac_uiaccess=True,
              icon=path.icon, name=path.output,
              upx=upx, strip=None, debug=debug, console=debug)
    # runtime_tmpdir='%HOMEPATH%\\AppData\\Local\\Temp\\' + name
else:
    exe = EXE(pyz, a.scripts, name=path.output, icon=path.icon,
              uac_admin=True, uac_uiaccess=True, upx=upx, strip=None,
              debug=debug, console=debug, exclude_binaries=1)
    dist = COLLECT(exe, a.binaries, a.zipfiles, a.datas,
                   upx=upx, strip=None, name=appname)
