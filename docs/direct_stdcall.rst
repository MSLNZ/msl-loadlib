.. _direct_stdcall:

Windows __stdcall
-----------------
Load a 32-bit Windows ``__stdcall`` library in 32-bit Python, see kernel32_.
Include the ``'windll'`` argument to specify that the calling convention is
``__stdcall``.

.. invisible-code-block: pycon

   >>> SKIP_IF_NOT_WINDOWS() or SKIP_IF_64BIT()

.. code-block:: pycon

   >>> from msl.loadlib import LoadLibrary
   >>> kernel = LoadLibrary(r'C:\Windows\SysWOW64\kernel32.dll', 'windll')
   >>> kernel
   <LoadLibrary libtype=WinDLL path=C:\Windows\SysWOW64\kernel32.dll>
   >>> kernel.lib
   <WinDLL 'C:\Windows\SysWOW64\kernel32.dll', handle ... at ...>
   >>> from ctypes import pointer
   >>> from msl.examples.loadlib.kernel32 import SystemTime
   >>> st = SystemTime()
   >>> time = kernel.lib.GetLocalTime(pointer(st))

Now that we have a SYSTEMTIME_ structure we can access its attributes

.. code-block:: pycon

   >>> from datetime import datetime
   >>> today = datetime.today()
   >>> st.wYear == today.year
   True
   >>> st.wMonth == today.month
   True
   >>> st.wDay == today.day
   True

See :ref:`here <tutorial_stdcall>` for an example on how to communicate with
kernel32_ from 64-bit Python.

.. _kernel32: https://www.geoffchappell.com/studies/windows/win32/kernel32/api/
.. _SYSTEMTIME: https://docs.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-systemtime
