"""Package constants."""

# pyright: reportUnreachable=false
from __future__ import annotations

import sys

__all__: list[str] = [
    "IS_LINUX",
    "IS_MAC",
    "IS_PYTHON_64BIT",
    "IS_WINDOWS",
    "default_extension",
    "server_filename",
]

IS_WINDOWS: bool = sys.platform == "win32"
"""Whether the operating system is Windows."""

IS_LINUX: bool = sys.platform.startswith("linux")
"""Whether the operating system is Linux."""

IS_MAC: bool = sys.platform == "darwin"
"""Whether the operating system is macOS."""

IS_PYTHON_64BIT: bool = sys.maxsize > 2**32
"""Whether the Python interpreter is 64-bits."""

server_filename: str
default_extension: str
if IS_WINDOWS:
    server_filename = "server32-windows.exe"
    default_extension = ".dll"
elif IS_LINUX:
    server_filename = "server32-linux"
    default_extension = ".so"
elif IS_MAC:
    server_filename = "server32-mac"
    default_extension = ".dylib"
else:
    server_filename = "server32-unknown"
    default_extension = ".unknown"
