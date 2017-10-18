"""
Load a shared library.

The following constants are provided in the **msl.loadlib** package.
"""
import sys
from collections import namedtuple

__author__ = 'Joseph Borbely'
__copyright__ = '\xa9 2017, ' + __author__
__version__ = '0.3.3.dev0'

version_info = namedtuple('version_info', 'major minor micro')(*map(int, __version__.split('.')[:3]))
""":obj:`~collections.namedtuple`: Contains the version information as a (major, minor, micro) tuple."""

IS_WINDOWS = sys.platform in ['win32', 'cygwin']
""":obj:`bool`: Whether the Operating System is Windows."""

IS_LINUX = sys.platform.startswith('linux')
""":obj:`bool`: Whether the Operating System is Linux."""

IS_MAC = sys.platform == 'darwin'
""":obj:`bool`: Whether the Operating System is Mac OS X."""

IS_PYTHON_64BIT = sys.maxsize > 2 ** 32
""":obj:`bool`: Whether the Python interpreter is 64-bits."""

IS_PYTHON2 = sys.version_info.major == 2
""":obj:`bool`: Whether Python 2.x is being used."""

IS_PYTHON3 = sys.version_info.major == 3
""":obj:`bool`: Whether Python 3.x is being used."""

if IS_WINDOWS:
    SERVER_FILENAME = 'server32-windows.exe'
    DEFAULT_EXTENSION = '.dll'
elif IS_LINUX:
    SERVER_FILENAME = 'server32-linux'
    DEFAULT_EXTENSION = '.so'
elif IS_MAC:
    SERVER_FILENAME = 'server32-mac'
    DEFAULT_EXTENSION = '.dylib'
else:
    SERVER_FILENAME = 'server32-unknown'
    DEFAULT_EXTENSION = '.unknown'

from .load_library import LoadLibrary
from .server32 import Server32
from .client64 import Client64
