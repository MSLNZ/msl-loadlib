"""Wrapper around the 32-bit Windows `__stdcall` library, [kernel32.dll]{:target="_blank"}.

Example of a server that loads a 32-bit Windows library, [kernel32.dll]{:target="_blank"},
in a 32-bit Python interpreter to host the library. The corresponding [Kernel64][] class
is created in a 64-bit Python interpreter and the [Kernel64][] class sends requests
to the [Kernel32][] class which calls the 32-bit library to execute the request and
then returns the response from the library.

!!! note
    This example is only valid on a Windows computer.

[kernel32.dll]: https://www.geoffchappell.com/studies/windows/win32/kernel32/api/
"""

from __future__ import annotations

import ctypes
from datetime import datetime

from msl.loadlib import Server32


class Kernel32(Server32):
    """Wrapper around the 32-bit Windows `__stdcall` library."""

    def __init__(self, host: str, port: int) -> None:
        """Wrapper around the 32-bit Windows `__stdcall` library, [kernel32.dll]{:target="_blank"}.

        [kernel32.dll]: https://www.geoffchappell.com/studies/windows/win32/kernel32/api/

        Args:
            host: The IP address (or hostname) to use for the server.
            port: The port to open for the server.
        """
        super().__init__("C:/Windows/SysWOW64/kernel32.dll", "windll", host, port)

    def get_local_time(self) -> datetime:
        """Calls the [kernel32.GetLocalTime]{:target="_blank"} function to get the current date and time.

        See the corresponding [Kernel64.get_local_time][msl.examples.loadlib.kernel64.Kernel64.get_local_time] method.

        [kernel32.GetLocalTime]: https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-getlocaltime

        Returns:
            The current date and time.
        """
        st = SystemTime()
        self.lib.GetLocalTime(ctypes.pointer(st))
        return datetime(
            st.wYear,
            month=st.wMonth,
            day=st.wDay,
            hour=st.wHour,
            minute=st.wMinute,
            second=st.wSecond,
            microsecond=st.wMilliseconds * 1000,
        )


class SystemTime(ctypes.Structure):
    """A [SYSTEMTIME]{:target="_blank"} [ctypes.Structure][]{:target="_blank"}.

    [SYSTEMTIME]: https://msdn.microsoft.com/en-us/library/windows/desktop/ms724950(v=vs.85).aspx
    """

    WORD = ctypes.c_uint16

    _fields_ = [
        ("wYear", WORD),
        ("wMonth", WORD),
        ("wDayOfWeek", WORD),
        ("wDay", WORD),
        ("wHour", WORD),
        ("wMinute", WORD),
        ("wSecond", WORD),
        ("wMilliseconds", WORD),
    ]
