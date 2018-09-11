import sys
from distutils.core import setup

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


setup(
    name='shairportmetadatareader',
    version='0.1.0',
    author='SchlaubiSchlump',
    packages=['shairportmetadatareader', 'shairportmetadatareader.remote'],
    license='GPLv3+',
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