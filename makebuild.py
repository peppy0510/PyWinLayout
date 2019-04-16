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


path = os.environ['PATH']
os.environ['PATH'] = ';'.join([path, os.path.join(path.split(';')[0], 'Scripts')])


class Build():

    @classmethod
    def run(self):
        # self.get_appname()
        self.set_version()
        self.remove_build()
        self.make_build()
        # self.run_test()
        self.make_installer()
        self.run_installer()

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
    def run_test(self):
        command = os.path.join(
            'dist', '{}.exe'.format(self.get_appname()))
        proc = subprocess.Popen(command, shell=True)
        proc.communicate()

    @classmethod
    def run_installer(self):
        command = os.path.join(
            'dist', '{} {}.exe'.format(
                self.get_appname(), self.get_version()))
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


if __name__ == '__main__':
    from io import TextIOWrapper
    sys.stdout = TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    Build.run()
