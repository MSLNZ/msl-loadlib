"""
A wrapper around the 32-bit Windows `kernel32.dll
<https://www.geoffchappell.com/studies/windows/win32/kernel32/api/>`_ library.

Example of a server that loads a 32-bit Windows library, `kernel32.dll <kernel_>`_,
in a 32-bit Python interpreter to host the library. The corresponding :mod:`~.kernel64`
module can be executed by a 64-bit Python interpreter and the :class:`~.kernel64.Kernel64`
class can send a request to the :class:`~.kernel32.Kernel32` class which calls the 32-bit
library to execute the request and then return the response from the library.

:class:`~.kernel32.Kernel32` is the 32-bit server and :class:`~.kernel64.Kernel64`
is the 64-bit client for `inter-process communication <ipc_>`_.

.. note::
   The `kernel32.dll <kernel_>`_ library is a standard Windows library and therefore
   this example is only valid on a Windows computer.

.. _ipc: https://en.wikipedia.org/wiki/Inter-process_communication
.. _kernel: https://www.geoffchappell.com/studies/windows/win32/kernel32/api/
"""
import ctypes
import datetime

from msl.loadlib import Server32


class Kernel32(Server32):

    def __init__(self, host, port, **kwargs):
        """
        Example of a class that is a wrapper around the Windows 32-bit `kernel32.dll
        <https://www.geoffchappell.com/studies/windows/win32/kernel32/api/>`_ library.

        Parameters
        ----------
        host : :class:`str`
            The IP address of the server.
        port : :class:`int`
            The port to open on the server.

        Note
        ----
        Any class that is a subclass of :class:`~msl.loadlib.server32.Server32` **MUST**
        provide two arguments in its constructor: `host` and `port` (in that order)
        and `**kwargs`. Otherwise the ``server32`` executable, see
        :class:`~msl.loadlib.start_server32`, cannot create an instance of the
        :class:`~msl.loadlib.server32.Server32` subclass.
        """
        super(Kernel32, self).__init__('C:/Windows/SysWOW64/kernel32.dll', 'windll', host, port)

    def get_time(self):
        """
        Calls the `kernel32.GetLocalTime
        <https://msdn.microsoft.com/en-us/library/windows/desktop/ms724338(v=vs.85).aspx>`_
        function to get the current date and time.

        See the corresponding 64-bit :meth:`~.kernel64.Kernel64.get_local_time` method.

        Returns
        -------
        :class:`~datetime.datetime` 
            The current date and time.
        """
        st = SystemTime()
        self.lib.GetLocalTime(ctypes.pointer(st))
        return datetime.datetime(st.wYear, month=st.wMonth, day=st.wDay,
                                 hour=st.wHour, minute=st.wMinute, second=st.wSecond,
                                 microsecond=st.wMilliseconds * 1000)


class SystemTime(ctypes.Structure):
    """Example of creating a :class:`ctypes.Structure`.

    See SYSTEMTIME_ for a description of the struct.

    .. _SYSTEMTIME: https://msdn.microsoft.com/en-us/library/windows/desktop/ms724950(v=vs.85).aspx
    """
    WORD = ctypes.c_uint16

    _fields_ = [('wYear', WORD),
                ('wMonth', WORD),
                ('wDayOfWeek', WORD),
                ('wDay', WORD),
                ('wHour', WORD),
                ('wMinute', WORD),
                ('wSecond', WORD),
                ('wMilliseconds', WORD)]
