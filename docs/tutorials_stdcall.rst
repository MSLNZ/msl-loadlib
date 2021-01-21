.. _tutorial_stdcall:

====================================================
Load a 32-bit **__stdcall** library in 64-bit Python
====================================================

This example shows how to access the 32-bit Windows kernel32_ library from
64-bit Python. :class:`~msl.examples.loadlib.kernel32.Kernel32` is the
32-bit server and :class:`~msl.examples.loadlib.kernel64.Kernel64` is the
64-bit client.

Create a :class:`~msl.examples.loadlib.kernel64.Kernel64` client to communicate
with the 32-bit kernel32_ library

.. invisible-code-block: pycon

   >>> SKIP_IF_NOT_WINDOWS()

.. code-block:: pycon

   >>> from msl.examples.loadlib import Kernel64
   >>> k = Kernel64()
   >>> k.lib32_path
   'C:\\Windows\\SysWOW64\\kernel32.dll'

Call the library to get the current date and time, see
:func:`~msl.examples.loadlib.kernel64.Kernel64.get_local_time`

.. code-block:: pycon

   >>> k.get_local_time()  # doctest: +SKIP
   datetime.datetime(2021, 1, 21, 15, 29, 8, 482000)

.. invisible-code-block: pycon

   >>> from datetime import datetime
   >>> assert isinstance(k.get_local_time(), datetime)

Shutdown the 32-bit server when you are done communicating with the 32-bit library

.. code-block:: pycon

   >>> stdout, stderr = k.shutdown_server32()

.. _kernel32: https://www.geoffchappell.com/studies/windows/win32/kernel32/api/
