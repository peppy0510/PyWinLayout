# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import os
import re
import shutil
import subprocess
import sys
import zipfile

from PIL import Image


path = os.environ['PATH']
os.environ['PATH'] = ';'.join([path, os.path.join(path.split(';')[0], 'Scripts')])


class Build():

    @classmethod
    def run(self, run_installer=True):
        self.make_icon()
        self.set_version()
        self.set_appname()
        self.set_api_ms_win_crt_path()
        self.remove_build()
        self.make_build()
        # self.run_build()
        self.make_installer()
        self.compress_installer()
        if run_installer:
            self.run_installer()

    @classmethod
    def make_icon(self):
        directory = os.path.join('assets', 'icon')
        src_path = os.path.join(directory, 'icon.png')
        dst_path = os.path.join(directory, 'icon.ico')
        icon_sizes = [(v, v) for v in (16, 24, 32, 48, 64, 96, 128, 256,)]
        img = Image.open(src_path)
        if os.path.exists(dst_path):
            os.remove(dst_path)
        img.save(dst_path, sizes=icon_sizes)

    @classmethod
    def remove_build(self):
        remove_paths = ['dist', 'build']
        for path in remove_paths:
            path = os.path.abspath(path)
            if os.path.isdir(path):
                try:
                    shutil.rmtree(path)
                    # print('removing %s' % (path))
                except Exception:
                    print('removing failed %s' % (path))

    @classmethod
    def subfile(self, ptrn, repl, path, **kwargs):
        if not os.path.exists(path):
            return

        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
            content = re.sub(ptrn, repl, content, **kwargs)

        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)

        return content

    @classmethod
    def make_build(self):
        proc = subprocess.Popen('pyinstaller makebuild.spec', shell=True)
        proc.communicate()

    @classmethod
    def get_appname(self):
        ptrn = (r'''[_]{0,2}appname[_]{0,2}[\s]{1,}[=]{1}[\s]{1,}'''
                r'''['"]{1}([a-zA-Z\s]{1,})['"]{1}''')
        with open(os.path.join('source', 'main.py'), 'r') as file:
            content = file.read()
            m = re.search(ptrn, content)
            if m:
                return m.group(1)

    @classmethod
    def set_appname(self):
        ptrn = (r'''(__appname__[\s]{1,}=[\s]{1,}[\'\"]{1})'''
                r'''[\w\d\s\-\_\.]{0,}([\'\"]{1})''')
        appname = self.get_appname()
        if appname:
            self.subfile(ptrn, r'\g<1>{}\g<2>'.format(appname), 'makebuild.spec')

    @classmethod
    def get_version(self):
        ptrn = (r'''[_]{0,2}version[_]{0,2}[\s]{1,}[=]{1}[\s]{1,}'''
                r'''['"]{1}([\d]{1,}\.[\d]{1,}\.[\d]{1,})['"]{1}''')
        with open(os.path.join('source', 'main.py'), 'r') as file:
            content = file.read()
            m = re.search(ptrn, content)
            if m:
                return m.group(1)

    @classmethod
    def set_version(self):
        ptrn = r'''([\d]{1,}\.[\d]{1,}\.[\d]{1,})'''
        version = self.get_version()
        if version:
            self.subfile(ptrn, version, 'makeinstaller.iss')

    @classmethod
    def set_api_ms_win_crt_path(self, architecture='amd64'):
        # 'x86' or 'amd64'
        existing_dirs = []
        basedir = 'C:\\Windows\\WinSxS'
        for dirname in os.listdir(basedir):
            if not dirname.startswith(architecture):
                continue
            absdir = os.path.join(basedir, dirname)
            if not os.path.isdir(absdir):
                continue

            for name in os.listdir(absdir):
                if 'api-ms-win-crt-' in name:
                    existing_dirs += [absdir]
        if not existing_dirs:
            return
        path = list(set(existing_dirs))[0]
        ptrn = (r'''(__api_ms_win_crt_path__[\s]{1,}=[\s]{1,}[\'\"]{1})'''
                r'''[\w\d\s\-\_\.\:\\]{0,}([\'\"]{1})''')
        path = path.replace('\\', '\\\\\\\\')
        self.subfile(ptrn, r'\g<1>{}\g<2>'.format(path), 'makebuild.spec')

    @classmethod
    def run_build(self):
        name = self.get_appname()
        command = '"{}"'.format(os.path.join('dist', '{}.exe'.format(name)))
        proc = subprocess.Popen(command, shell=True)
        proc.communicate()

    @classmethod
    def make_installer(self):
        for name in os.listdir('dist'):
            if os.path.splitext(name)[0][-1].isdigit():
                os.remove(os.path.join('dist', name))

        issc = r'''"C:\\Program Files (x86)\\Inno Setup 5\\ISCC.exe"'''
        command = '''%s "makeinstaller.iss"''' % (issc)
        proc = subprocess.Popen(command, shell=True)
        proc.communicate()

    @classmethod
    def get_installer_name(self):
        with open('makeinstaller.iss', 'r') as file:
            for line in file.read().split('\n'):
                if line.startswith('OutputBaseFilename'):
                    return line.split('=')[-1].strip()

    @classmethod
    def compress_installer(self):
        name = self.get_installer_name()
        if not name:
            return
        src_name = '{}.exe'.format(name)
        src_path = os.path.join('dist', src_name)
        dst_path = os.path.join('dist', '{}.zip'.format(name))
        file = zipfile.ZipFile(dst_path, 'w', zipfile.ZIP_DEFLATED)
        file.write(src_path, src_name)
        # zipdir('tmp/', zipf)
        file.close()
        # for root, dirs, files in os.walk(path):
        #     for file in files:
        #         ziph.write(os.path.join(root, file))

    @classmethod
    def run_installer(self):
        name = self.get_installer_name()
        if not name:
            return
        command = '"{}"'.format(os.path.join('dist', name))
        proc = subprocess.Popen(command, shell=True)
        proc.communicate()


if __name__ == '__main__':
    from io import TextIOWrapper
    sys.stdout = TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    Build.run()
