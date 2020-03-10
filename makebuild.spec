# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import glob
import os


debug = False

upx = True
onefile = True
uac_admin = False
uac_uiaccess = True


PYZ = PYZ  # noqa
EXE = EXE  # noqa
COLLECT = COLLECT  # noqa
Analysis = Analysis  # noqa


__appname__ = 'PyWinLayout'
__api_ms_win_crt_path__ = 'C:\\Windows\\WinSxS\\amd64_microsoft-windows-m..namespace-downlevel_31bf3856ad364e35_10.0.18362.1_none_99c24aabfe52bcbb'


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
    base=os.path.join('source', 'base'),
    assets=os.path.join('assets'),
    icon=os.path.join('assets', 'icon', 'icon.ico'),
    dlls=os.path.join('assets', 'dlls'),
    output=os.path.join('build', '{}.exe'.format(__appname__)),
    winsxs=__api_ms_win_crt_path__
)

a = Analysis([os.path.join('source', 'main.pyw')],
             hookspath=[path.home, path.base, path.assets],
             pathex=[path.home, path.assets, path.dlls, path.winsxs],
             hiddenimports=['base'])

a.datas += grapdatas(path.assets, 'icon', 2, 'data', ['icon.ico'])
# a.datas += [('PyWinLayout.exe.manifest', 'PyWinLayout.exe.manifest', 'data')]
# a.datas += grapdatas(path.assets, 'dlls', 2, 'data', ['API-MS-Win-core-file-l2-1-0.dll'])

print('-' * 100)
for v in a.datas:
    print(v)
print('-' * 100)

pyz = PYZ(a.pure)

if onefile:
    exe = EXE(pyz, a.scripts + [('O', '', 'OPTION')],
              a.binaries, a.zipfiles, a.datas,
              name=path.output, icon=path.icon,
              uac_admin=uac_admin, uac_uiaccess=uac_uiaccess,
              upx=upx, strip=None, debug=debug, console=debug)
    # runtime_tmpdir='%HOMEPATH%\\AppData\\Local\\Temp\\' + name
else:
    exe = EXE(pyz, a.scripts, name=path.output, icon=path.icon,
              uac_admin=uac_admin, uac_uiaccess=uac_uiaccess,
              upx=upx, strip=None, debug=debug, console=debug,
              exclude_binaries=1)
    dist = COLLECT(exe, a.binaries, a.zipfiles, a.datas,
                   upx=upx, strip=None, name=__appname__)
