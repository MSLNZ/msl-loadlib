"""
Load a shared library.

The following constants are provided in the **msl.loadlib** package.
"""
import re
import sys
from collections import namedtuple

__author__ = 'Joseph Borbely'
__copyright__ = '\xa9 2017, ' + __author__
__version__ = '0.2.0-dev'

version_info = namedtuple('version_info', 'major minor micro releaselevel')(*(int(v) if v.isdigit() else v for v in re.split('[. -]', __version__)))
""":py:func:`~collections.namedtuple`: Contains the version information as a (major, minor, micro, releaselevel) tuple."""

IS_WINDOWS = sys.platform in ['win32', 'cygwin']
""":py:class:`bool`: Whether the Operating System is Windows."""

IS_LINUX = sys.platform.startswith('linux')
""":py:class:`bool`: Whether the Operating System is Linux."""

IS_MAC = sys.platform == 'darwin'
""":py:class:`bool`: Whether the Operating System is Mac OS X."""

IS_PYTHON_64BIT = sys.maxsize > 2 ** 32
""":py:class:`bool`: Whether the Python interpreter is 64-bits."""

IS_PYTHON2 = sys.version_info.major == 2
""":py:class:`bool`: Whether Python 2.x is being used."""

IS_PYTHON3 = sys.version_info.major == 3
""":py:class:`bool`: Whether Python 3.x is being used."""

if IS_WINDOWS:
    SERVER_FILENAME = 'server32-windows.exe'
elif IS_LINUX:
    SERVER_FILENAME = 'server32-linux'
elif IS_MAC:
    SERVER_FILENAME = 'server32-mac'
else:
    SERVER_FILENAME = 'server32-unknown'

from .load_library import LoadLibrary
from .server32 import Server32
from .client64 import Client64
