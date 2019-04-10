"""
setup.py to 'build', 'install' and 'test' this package.
Usage: python setup.py 'command'
"""

import subprocess
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
import os

# dynamically build requirements for either kivy or eventdispatcher depending on which library is installed.
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

custom_user_options = [
    ("with-mqtt", None, "Set this flag to add support for the mqtt backend."),
]

custom_boolean_options = [
    "with-mqtt"
]

class CustomInstallCommand(install):
    user_options = install.user_options + custom_user_options

    boolean_options = install.boolean_options + custom_boolean_options

    def initialize_options(self):
        install.initialize_options(self)
        self.with_mqtt = 0

    def finalize_options(self):
        install.finalize_options(self)

    def run(self):
        if self.with_mqtt:
            global requirements
            requirements += ["paho-mqtt"]
        install.run(self)


class CustomInstallDevelopCommand(develop):
    user_options = develop.user_options + custom_user_options

    boolean_options = develop.boolean_options + custom_boolean_options

    def initialize_options(self):
        develop.initialize_options(self)
        self.with_mqtt = 0

    def finalize_options(self):
        develop.finalize_options(self)

    def run(self):
        if self.with_mqtt:
            global requirements
            requirements += ["paho-mqtt"]
        develop.run(self)


class CustomInstallEggInfoCommand(egg_info):
    user_options = egg_info.user_options + custom_user_options

    boolean_options = egg_info.boolean_options + custom_boolean_options

    def initialize_options(self):
        egg_info.initialize_options(self)
        self.with_mqtt = 0

    def finalize_options(self):
        egg_info.finalize_options(self)

    def run(self):
        print(self.with_mqtt)
        if self.with_mqtt:
            global requirements
            requirements += ["paho-mqtt"]
        print("eggInfo: ", requirements)
        egg_info.run(self)


class CustomTestCommand(TestCommand):
    """
    Class to run testcases for kivy as well as for eventdispatcher backend.
    """

    def run(self):
        try:
            import kivy
            # kivy is installed => run the tests with kivy
            os.environ["PREFER_KIVY"] = "1"
            print("running tests with kivy:")
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
    version='0.1.0b1',
    author='SchlaubiSchlump',
    packages=['shairportmetadatareader', 'shairportmetadatareader.remote', 'shairportmetadatareader.listener'],
    license='GPLv3+',
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    cmdclass={
        'test': CustomTestCommand,
        'install': CustomInstallCommand,
        'develop': CustomInstallDevelopCommand,
        'egg_info': CustomInstallEggInfoCommand
    },
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
    keywords='music airplay shairport shairport-sync dmap daap remote metadata mqtt-client mqtt',
)