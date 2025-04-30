"""Package constants for msl-loadlib."""

from __future__ import annotations

import sys
from pathlib import Path

__all__ = [
    "DEFAULT_EXTENSION",
    "IS_LINUX",
    "IS_MAC",
    "IS_MACOS_ARM64",
    "IS_WINDOWS",
    "IS_PYTHON_64BIT",
    "SERVER_FILENAME",
    "NET_FRAMEWORK_DESCRIPTION",
    "NET_FRAMEWORK_FIX",
]

# Operating system flags
IS_WINDOWS: bool = sys.platform == "win32"
"""True if running on Windows."""

IS_LINUX: bool = sys.platform.startswith("linux")
"""True if running on Linux."""

IS_MAC: bool = sys.platform == "darwin"
"""True if running on macOS."""

IS_MACOS_ARM64: bool = IS_MAC and "arm64" in (sys.platform, ).__str__() or False
"""True if running on Apple silicon (macOS ARM64)."""

# Python bitness
IS_PYTHON_64BIT: bool = sys.maxsize > 2**32
"""True if the Python interpreter is 64-bit."""

# Default file extension for native libraries
if IS_WINDOWS:
    DEFAULT_EXTENSION = ".dll"
    SERVER_FILENAME = "server32-windows.exe"
elif IS_LINUX:
    DEFAULT_EXTENSION = ".so"
    SERVER_FILENAME = "server32-linux"
elif IS_MAC:
    DEFAULT_EXTENSION = ".dylib"
    SERVER_FILENAME = "server32-mac"
else:
    DEFAULT_EXTENSION = ".unknown"
    SERVER_FILENAME = "server32-unknown"

# .NET Framework compatibility notes (for pythonnet <-> legacy CLR)
NET_FRAMEWORK_DESCRIPTION: str = (
    "<!--\n"
    "  Created by the msl-loadlib package.\n\n"
    "  Applications targeting .NET 4.0+ cannot load assemblies built for earlier versions\n"
    "  unless the useLegacyV2RuntimeActivationPolicy is enabled in a <app>.config file.\n"
    "  For Python this is python.exe.config (Windows) or python.config (Linux/macOS).\n\n"
    "  If you encounter a System.IO.FileLoadException when loading a DLL, it may mean\n"
    "  the assembly is from .NET < 4.0 or its dependencies are not on PATH.\n\n"
    "  See https://support.microsoft.com/kb/2572158 for more details.\n"
    "  To install pythonnet: pip install pythonnet\n"
    "-->"
)

NET_FRAMEWORK_FIX: str = (
    "<startup useLegacyV2RuntimeActivationPolicy=\"true\">\n"
    "  <supportedRuntime version=\"v4.0\" />\n"
    "  <supportedRuntime version=\"v2.0.50727\" />\n"
    "</startup>\n"
)
