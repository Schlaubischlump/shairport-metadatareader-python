"""
setup.py to 'build', 'install' and 'test' this package.
Usage: python setup.py 'command'
"""
import os
import sys
import subprocess
from setuptools import setup
from setuptools.command.test import test as TestCommand

# pylint: disable=C0103

# dynamically build requirements for either kivy or eventdispatcher depending on which library is installed.
IS_PY2 = sys.version_info.major <= 2

requirements = ["requests"]
# zeroconf version 0.20.0 dropped support for python 2
requirements += ["zeroconf==0.19.1", "enum34"] if IS_PY2 else ["zeroconf"]

# if kivy is installed we don't need to download eventdispatcher
try:
    import kivy
    kivy.require("1.1.0")
except Exception: # pylint: disable=W0703
    requirements += ["eventdispatcher"]


class CustomTestCommand(TestCommand):
    """
    Class to run testcases for kivy as well as for eventdispatcher backend.
    """

    def run(self):
        try:
            import kivy # pylint: disable=W0621, W0611
            # kivy is installed => run the tests with kivy
            os.environ["PREFER_KIVY"] = "1"
            print("running tests with kivy:")
            self._run(['pytest', '.'])
        except ImportError:
            pass

        try:
            import eventdispatcher  # pylint: disable=W0611
            # eventdispatcher is installed => run the tests with eventdispatcher
            os.environ["PREFER_KIVY"] = "0"
            print("running tests with eventdispatcher:")
            self._run(['pytest', '.'])
        except ImportError:
            pass

    def _run(self, command):
        # pylint: disable=R0201
        try:
            subprocess.check_call(command)
        except subprocess.CalledProcessError as error:
            print('Command failed with exit code', error.returncode)
            sys.exit(error.returncode)


setup(
    name='shairportmetadatareader',
    version='0.1.0b2',
    author='SchlaubiSchlump',
    packages=['shairportmetadatareader', 'shairportmetadatareader.remote', 'shairportmetadatareader.listener'],
    license='GPLv3+',
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    cmdclass={
        'test': CustomTestCommand
    },
    long_description=open('Readme.md').read(),
    install_requires=requirements,
    classifiers=[
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
    keywords='music airplay shairport shairport-sync dmap daap remote metadata mqtt-client mqtt',
)
