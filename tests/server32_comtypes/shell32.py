# When the 32-bit server was running in Python 3.9.1 loading
# Scripting.FileSystemObject (in ctypes_union_error.py) raised
# errors from comtypes that were not related to the ctypes error.
#
# This test class can be used to replace ctypes_union_error.py
# to test that comtypes can load a library on the 32-bit server.
# We don't want to test the code of comtypes just MSL-LoadLib
#

from __future__ import annotations

from typing import Callable

from msl.loadlib import Server32


class Shell32(Server32):
    def __init__(self, host: str, port: int) -> None:
        # comtypes will try to import numpy to see if it is available.
        # Since Client64 passes its sys.path to Server32 the modules that
        # are available to Client64 to import are also available to Server32.
        # Therefore, we don't want this test to fail because the Python
        # environment that is running Client64 has numpy installed.
        # (This only appeared to be an issue when Client64 runs on Python 3.5)
        _ = Server32.remove_site_packages_64bit()

        super().__init__("WScript.Shell", "com", host, port)

        self._environ: Callable[[str], str] = self.lib.Environment("System")

    def environ(self, name: str) -> str:
        value: str = self._environ(name)
        return value
