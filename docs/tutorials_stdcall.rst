.. _tutorial_stdcall:

========================================================
Load a 32-bit Windows *stdcall* library in 64-bit Python
========================================================

This example shows how to access the 32-bit Windows `kernel32 <kernel32_>`_ library, from a
module that is run by a 64-bit Python interpreter by using `inter-process communication
<https://en.wikipedia.org/wiki/Inter-process_communication>`_.
:class:`~msl.examples.loadlib.kernel32.Kernel32` is the 32-bit server and
:class:`~msl.examples.loadlib.kernel64.Kernel64` is the 64-bit client.

The following shows that the `kernel32 <kernel32_>`_ library cannot be loaded in a 64-bit
Python interpreter:

.. code-block:: python

   >>> from msl.loadlib import LoadLibrary, IS_PYTHON_64BIT
   >>> IS_PYTHON_64BIT
   True
   >>> k = LoadLibrary('C:/Windows/SysWOW64/kernel32.dll', 'windll')
   Traceback (most recent call last):
     File "<input>", line 1, in <module>
     File "D:\code\git\msl-loadlib\msl\loadlib\load_library.py", line 62, in __init__
       self._lib = ctypes.WinDLL(self._path)
     File "C:\Users\j.borbely\Miniconda3\lib\ctypes\__init__.py", line 347, in __init__
       self._handle = _dlopen(self._name, mode)
   OSError: [WinError 193] %1 is not a valid Win32 application

Instead, create a :class:`~msl.examples.loadlib.kernel64.Kernel64` client to communicate with the
32-bit `kernel32 <kernel32_>`_ library:

.. code-block:: python

   >>> from msl.examples.loadlib import Kernel64
   >>> k = Kernel64()
   >>> k
   Kernel64 object at 0x1798a792940 hosting kernel32.dll on http://127.0.0.1:59481
   >>> k.lib32_path
   'C:\\Windows\\SysWOW64\\kernel32.dll'

Call the library to get the current date and time, see
:func:`~msl.examples.loadlib.kernel64.Kernel64.get_local_time`:

.. code-block:: python

   >>> k.get_local_time()
   datetime.datetime(2017, 2, 3, 16, 37, 5, 351000)

Shutdown the server, see :meth:`~msl.loadlib.client64.Client64.shutdown_server32`:

.. code-block:: python

   >>> k.shutdown_server32()

.. note::
   When using a subclass of :class:`~msl.loadlib.client64.Client64` in a script, the
   :meth:`~msl.loadlib.client64.Client64.shutdown_server32` method gets called automatically
   when the instance of the subclass is about to be destroyed and therefore you do not have to call
   the :meth:`~msl.loadlib.client64.Client64.shutdown_server32` method to shutdown the server.

.. _kernel32: http://www.geoffchappell.com/studies/windows/win32/kernel32/api/