import subprocess
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand
import os

# dynamically build requirements because of kivy/eventdispatcher dependency
IS_PY2 = sys.version_info.major <= 2

requirements = ["requests"]
# zeroconf version 0.20.0 dropped support for python 2
requirements += ["zeroconf==0.19.1", "enum34"] if IS_PY2 else ["zeroconf"]

# if kivy is installed we don't need to download eventdispatcher
try:
    import kivy
    kivy.require("1.1.0")
except:
    requirements += ["eventdispatcher"]


class TestCommand(TestCommand):

    description = 'run linters, tests and create a coverage report'
    user_options = []

    def run(self):
        try:
            import kivy
            # kivy is installed => run the tests with kivy
            os.environ["PREFER_KIVY"] = "1"
            print("running tests with Kivy:")
            self._run(['pytest', '.'])
        except ImportError:
            pass

        try:
            import eventdispatcher
            # eventdispatcher is installed => run the tests with eventdispatcher
            os.environ["PREFER_KIVY"] = "0"
            print("running tests with eventdispatcher:")
            self._run(['pytest', '.'])
        except ImportError:
            pass




    def _run(self, command):
        try:
            subprocess.check_call(command)
        except subprocess.CalledProcessError as error:
            print('Command failed with exit code', error.returncode)
            sys.exit(error.returncode)

setup(
    name='shairportmetadatareader',
    version='0.1.1',
    author='SchlaubiSchlump',
    packages=['shairportmetadatareader', 'shairportmetadatareader.remote'],
    license='GPLv3+',
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    cmdclass={'test': TestCommand},
    long_description=open('Readme.md').read(),
    install_requires=requirements,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',  # untested
        'Programming Language :: Python :: 3.5',  # untested
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',  # untested
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Multimedia',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Software Development :: Libraries'
        'Topic :: Utilities'
    ],
    keywords='music airplay shairport shairport-sync dmap daap remote metadata',
)