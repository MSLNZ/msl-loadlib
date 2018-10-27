"""
Communicates with `kernel32.dll
<https://www.geoffchappell.com/studies/windows/win32/kernel32/api/>`_ via
the :class:`~.kernel32.Kernel32` class.

Example of a module that can be executed by a 64-bit Python interpreter which can
communicate with a Windows 32-bit library, `kernel32.dll <kernel_>`_, that is hosted by the
corresponding 32-bit Python server, :mod:`.kernel32`.

:class:`~.kernel64.Kernel64` is the 64-bit client and :class:`~.kernel32.Kernel32`
is the 32-bit server for `inter-process communication <ipc_>`_.

.. note::
   The `kernel32.dll <kernel_>`_ library is a standard Windows library and therefore this
   example is only valid on a computer running Windows.

.. _ipc: https://en.wikipedia.org/wiki/Inter-process_communication
.. _kernel: https://www.geoffchappell.com/studies/windows/win32/kernel32/api/
"""
import os

from msl.loadlib import Client64


class Kernel64(Client64):
    """
    Example of a class that can communicate with the 32-bit `kernel32.dll
    <https://www.geoffchappell.com/studies/windows/win32/kernel32/api/>`_ library.

    This class demonstrates how to communicate with a Windows 32-bit library if an
    instance of this class is created within a 64-bit Python interpreter.
    """
    def __init__(self):
        # specify the name of the corresponding 32-bit server module, kernel32, which hosts
        # the Windows 32-bit library -- kernel32.dll
        super(Kernel64, self).__init__(module32='kernel32', append_sys_path=os.path.dirname(__file__))

    def get_local_time(self):
        """
        Sends a request to the 32-bit server, :class:`~.kernel32.Kernel32`, to
        execute the `kernel32.GetLocalTime <time_>`_ function to get the
        current date and time.

        See the corresponding 32-bit :meth:`~.kernel32.Kernel32.get_time` method.

        .. _time: https://msdn.microsoft.com/en-us/library/windows/desktop/ms724338(v=vs.85).aspx

        Returns
        -------
        :class:`~datetime.datetime` 
            The current date and time.
        """
        return self.request32('get_time')
