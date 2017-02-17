"""
Load a shared library.

The following constants are provided in the **msl.loadlib** package.
"""
import sys
import time
from collections import namedtuple

version_info = namedtuple('version_info', 'major minor micro releaselevel')(0, 1, 0, 'beta')
""":func:`~collections.namedtuple`: Contains the version information as a (major, minor, micro, releaselevel) tuple."""

__version__ = '{}.{}.{}'.format(*version_info)
__author__ = 'Joseph Borbely'
__copyright__ = '\xa9 2017{}, {}'.format(time.strftime('-%Y') if int(time.strftime('%Y')) > 2017 else '', __author__)

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

from .load_library import LoadLibrary
from .server32 import Server32
from .client64 import Client64
