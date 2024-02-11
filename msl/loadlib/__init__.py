"""
Load a shared library.
"""
import sys

from . import utils
from ._version import __version__
from ._version import __version_info__
from .client64 import Client64
from .exceptions import ConnectionTimeoutError
from .exceptions import ResponseTimeoutError
from .exceptions import Server32Error
from .load_library import LoadLibrary
from .server32 import Server32

__author__: str = 'Measurement Standards Laboratory of New Zealand'
__copyright__: str = f'\xa9 2017 - 2024, {__author__}'

version_info = __version_info__
"""Contains the version information as a (major, minor, micro, releaselevel) named tuple."""

if not hasattr(sys, 'coinit_flags'):
    # Configure comtypes to use COINIT_MULTITHREADED when it is imported.
    # This avoids the following exception from being raised:
    #   [WinError -2147417850] Cannot change thread mode after it is set
    sys.coinit_flags = 0x0
