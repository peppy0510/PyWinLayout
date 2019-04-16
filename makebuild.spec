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


def find_api_ms_win_crt_path(architecture='amd64'):
    # 'x86' or 'amd64'
    existing_dirs = []
    basedir = os.path.join('C:\\Windows\\WinSxS')
    for dirname in os.listdir(basedir):
        if not dirname.startswith(architecture):
            continue
        absdir = os.path.join(basedir, dirname)
        if not os.path.isdir(absdir):
            continue

        for name in os.listdir(absdir):
            if 'api-ms-win-crt-' in name:
                existing_dirs += [absdir]

    return list(set(existing_dirs))[0]


path = Path(
    home='',
    base=os.path.join('source', 'base'),
    assets='assets',
    icon=os.path.join('assets', 'icon', 'icon.ico'),
    dlls=os.path.join('assets', 'dlls'),
    output=os.path.join('build', '{}.exe'.format(appname)),
    winsxs=find_api_ms_win_crt_path()
)

a = Analysis([os.path.join('source', 'main.py')],
             hookspath=[path.home, path.base, path.assets],
             pathex=[path.home, path.assets, path.dlls, path.winsxs],
             hiddenimports=['base'])

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
