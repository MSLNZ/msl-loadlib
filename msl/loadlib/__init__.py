"""
Load a shared library.
"""
import sys

if not hasattr(sys, 'coinit_flags'):
    # Configure comtypes to use COINIT_MULTITHREADED when it is imported.
    # This avoids the following exception from being raised:
    #   [WinError -2147417850] Cannot change thread mode after it is set
    sys.coinit_flags = 0x0

from . import utils
from ._version import __version__
from ._version import version_info
from .client64 import Client64
from .exceptions import ConnectionTimeoutError
from .exceptions import ResponseTimeoutError
from .exceptions import Server32Error
from .load_library import LoadLibrary
from .server32 import Server32

__author__ = 'Measurement Standards Laboratory of New Zealand'
__copyright__ = f'\xa9 2017 - 2023, {__author__}'
