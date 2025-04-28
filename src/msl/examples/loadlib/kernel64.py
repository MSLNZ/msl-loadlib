"""Communicate with the [kernel32.dll]{:target="_blank"} library via the [Kernel32][] class that is running on a server.

!!! note
    This example is only valid on a Windows computer.

[kernel32.dll]: https://www.geoffchappell.com/studies/windows/win32/kernel32/api/
"""

from __future__ import annotations

import os
from datetime import datetime

from msl.loadlib import Client64


class Kernel64(Client64):
    """Communicate with a 32-bit Windows `__stdcall` library."""

    def __init__(self) -> None:
        """Communicate with a 32-bit Windows `__stdcall` library, [kernel32.dll]{:target="_blank"}.

        This class demonstrates how to communicate with a Windows 32-bit library if an
        instance of this class is created within a 64-bit Python interpreter.

        [kernel32.dll]: https://www.geoffchappell.com/studies/windows/win32/kernel32/api/
        """
        # specify the name of the corresponding 32-bit server module, kernel32, which hosts
        # the Windows 32-bit library -- kernel32.dll
        super().__init__(module32="kernel32", append_sys_path=os.path.dirname(__file__))

    def get_local_time(self) -> datetime:
        """Requests [kernel32.GetLocalTime]{:target="_blank"} function to get the current date and time.

        See the corresponding [Kernel32.get_local_time][msl.examples.loadlib.kernel32.Kernel32.get_local_time] method.

        [kernel32.GetLocalTime]: https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-getlocaltime

        Returns:
            The current date and time.
        """
        return self.request32("get_local_time")
