"""Load a library."""

from __future__ import annotations

from .__about__ import __author__, __copyright__, __version__, version_tuple
from .client64 import Client64
from .constants import IS_PYTHON_64BIT
from .exceptions import ConnectionTimeoutError, ResponseTimeoutError, Server32Error
from .load_library import LoadLibrary
from .server32 import Server32
from .utils import generate_com_wrapper, get_com_info

__all__: list[str] = [
    "IS_PYTHON_64BIT",
    "Client64",
    "ConnectionTimeoutError",
    "LoadLibrary",
    "ResponseTimeoutError",
    "Server32",
    "Server32Error",
    "__author__",
    "__copyright__",
    "__version__",
    "generate_com_wrapper",
    "get_com_info",
    "version_tuple",
]
