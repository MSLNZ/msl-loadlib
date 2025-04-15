"""
Package constants.
"""

from __future__ import annotations

import sys

__all__: list[str] = [
    "DEFAULT_EXTENSION",
    "IS_LINUX",
    "IS_MAC",
    "IS_WINDOWS",
    "IS_PYTHON_64BIT",
    "NET_FRAMEWORK_DESCRIPTION",
    "NET_FRAMEWORK_FIX",
    "SERVER_FILENAME",
]

IS_WINDOWS: bool = sys.platform == "win32"
"""Whether the operating system is Windows."""

IS_LINUX: bool = sys.platform.startswith("linux")
"""Whether the operating system is Linux."""

IS_MAC: bool = sys.platform == "darwin"
"""Whether the operating system is macOS."""

IS_PYTHON_64BIT: bool = sys.maxsize > 2**32
"""Whether the Python interpreter is 64-bits."""

SERVER_FILENAME: str
DEFAULT_EXTENSION: str
if IS_WINDOWS:
    SERVER_FILENAME = "server32-windows.exe"
    DEFAULT_EXTENSION = ".dll"
elif IS_LINUX:
    SERVER_FILENAME = "server32-linux"
    DEFAULT_EXTENSION = ".so"
elif IS_MAC:
    SERVER_FILENAME = "server32-mac"
    DEFAULT_EXTENSION = ".dylib"
else:
    SERVER_FILENAME = "server32-unknown"
    DEFAULT_EXTENSION = ".unknown"


NET_FRAMEWORK_DESCRIPTION: str = """
<!--
  Created by the MSL-LoadLib package.

  By default, applications that target the .NET Framework version 4.0+ cannot load
  assemblies from previous .NET Framework versions. You must add and modify the
  <app>.config file and set the useLegacyV2RuntimeActivationPolicy property to be
  "true". For the Python executable this would be a python.exe.config (Windows) 
  or python.config (Linux) configuration file.

  Python for .NET (https://pythonnet.github.io/) works with .NET 4.0+ and 
  therefore it cannot automatically load a shared library that was compiled with
  .NET < 4.0. If you try to load the library and a System.IO.FileLoadException is
  raised then that might mean that the library is from .NET < 4.0.

  The System.IO.FileLoadException exception could also be raised if the directory
  that the DLL is located in, or a dependency of the library, is not within PATH. 

  See https://support.microsoft.com/kb/2572158 for an overview.

  NOTE: To install pythonnet, run:
  $ pip install pythonnet
-->
"""

NET_FRAMEWORK_FIX: str = """
    <startup useLegacyV2RuntimeActivationPolicy="true">
        <supportedRuntime version="v4.0" />
        <supportedRuntime version="v2.0.50727" />
    </startup>
"""
