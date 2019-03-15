"""
Load a shared library.

The following constants are provided in the **MSL-LoadLib** package.
"""
import re
import sys
from collections import namedtuple

__author__ = 'Joseph Borbely'
__copyright__ = '\xa9 2017 - 2019, ' + __author__
__version__ = '0.5.1.dev0'

_v = re.search(r'(\d+)\.(\d+)\.(\d+)[.-]?(.*)', __version__).groups()

version_info = namedtuple('version_info', 'major minor micro releaselevel')(int(_v[0]), int(_v[1]), int(_v[2]), _v[3])
""":obj:`~collections.namedtuple`: Contains the version information as a (major, minor, micro, releaselevel) tuple."""

IS_WINDOWS = sys.platform in ['win32', 'cygwin']
""":class:`bool`: Whether the Operating System is Windows."""

IS_LINUX = sys.platform.startswith('linux')
""":class:`bool`: Whether the Operating System is Linux."""

IS_MAC = sys.platform == 'darwin'
""":class:`bool`: Whether the Operating System is Mac OS X."""

IS_PYTHON_64BIT = sys.maxsize > 2 ** 32
""":class:`bool`: Whether the Python interpreter is 64-bits."""

IS_PYTHON2 = sys.version_info.major == 2
""":class:`bool`: Whether Python 2.x is being used."""

IS_PYTHON3 = sys.version_info.major == 3
""":class:`bool`: Whether Python 3.x is being used."""

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

from . import utils
from .load_library import LoadLibrary
from .client64 import Client64
from .server32 import Server32

from .exceptions import Server32Error
from .exceptions import ConnectionTimeoutError
from .exceptions import ServerExit
