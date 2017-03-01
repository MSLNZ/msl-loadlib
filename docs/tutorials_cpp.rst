.. _tutorial_cpp:

==========================================
Load a 32-bit C++ library in 64-bit Python
==========================================

.. note::
   If you have issues running the example please make sure that you have the
   :ref:`prerequisites <prerequisites>` installed.

This example shows how to access a 32-bit C++ library from a module that is run by a
64-bit Python interpreter by using `inter-process communication
<https://en.wikipedia.org/wiki/Inter-process_communication>`_.
:class:`~msl.examples.loadlib.cpp32.Cpp32` is the 32-bit server and
:class:`~msl.examples.loadlib.cpp64.Cpp64` is the 64-bit client. The source
code of the C++ program is available :ref:`here <cpp-lib>`.

.. important::
   By default :py:mod:`ctypes` expects that a :py:class:`ctypes.c_int` data type is
   returned from the library call. If the returned value from the library is not a
   :py:class:`ctypes.c_int` then you **MUST** redefine the ctypes `restype`_ value
   to be the appropriate data type. The :class:`~msl.examples.loadlib.cpp32.Cpp32`
   class shows various examples of redefining the `restype`_ value.

.. _restype: https://docs.python.org/3/library/ctypes.html#ctypes._FuncPtr.restype

The following shows that the :ref:`cpp_lib32 <cpp-lib>` library
cannot be loaded in a 64-bit Python interpreter:

.. code-block:: python

   >>> import os
   >>> from msl.loadlib import LoadLibrary, EXAMPLES_DIR, IS_PYTHON_64BIT
   >>> IS_PYTHON_64BIT
   True
   >>> cpp = LoadLibrary(os.path.join(EXAMPLES_DIR, 'cpp_lib32'))
   Traceback (most recent call last):
     File "<input>", line 1, in <module>
     File "D:\code\git\msl-loadlib\msl\loadlib\load_library.py", line 60, in __init__
       self._lib = ctypes.CDLL(self._path)
     File "C:\Users\j.borbely\Miniconda3\lib\ctypes\__init__.py", line 347, in __init__
       self._handle = _dlopen(self._name, mode)
   OSError: [WinError 193] %1 is not a valid Win32 application

However, the 64-bit version of the C++ library can be directly loaded in 64-bit Python:

.. code-block:: python

   >>> cpp64 = LoadLibrary(os.path.join(EXAMPLES_DIR, 'cpp_lib64'))
   >>> cpp64
   LoadLibrary object at 0x11558dbd898; libtype=CDLL; path=D:\code\git\msl-loadlib\msl\examples\loadlib\cpp_lib64.dll
   >>> cpp64.lib.add(3, 14)
   17

Instead, create a :class:`~msl.examples.loadlib.cpp64.Cpp64` client to communicate with the
32-bit :ref:`cpp_lib32 <cpp-lib>` library from 64-bit Python:

.. code-block:: python

   >>> from msl.examples.loadlib import Cpp64
   >>> cpp = Cpp64()
   >>> cpp
   Cpp64 object at 0x1798a79af60 hosting cpp_lib32.dll on http://127.0.0.1:16517
   >>> cpp.lib32_path
   'D:\\code\\git\\msl-loadlib\\msl\\examples\\loadlib\\cpp_lib32.dll'

Add two integers, see :meth:`~msl.examples.loadlib.cpp64.Cpp64.add`:

.. code-block:: python

   >>> cpp.add(3, 14)
   17

Subtract two C++ floating-point numbers, see :meth:`~msl.examples.loadlib.cpp64.Cpp64.subtract`:

.. code-block:: python

   >>> cpp.subtract(43.2, 3.2)
   40.0

Add or subtract two C++ double-precision numbers, see :meth:`~msl.examples.loadlib.cpp64.Cpp64.add_or_subtract`:

.. code-block:: python

   >>> cpp.add_or_subtract(1.1, 2.2, True)
   3.3000000000000003
   >>> cpp.add_or_subtract(1.1, 2.2, False)
   -1.1

Multiply a 1D array by a number, see :meth:`~msl.examples.loadlib.cpp64.Cpp64.scalar_multiply`:

.. code-block:: python

   >>> a = [float(val) for val in range(10)]
   >>> a
   [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
   >>> cpp.scalar_multiply(2.0, a)
   [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0]

Reverse a string. The memory for the reversed string is allocated in Python,
see :meth:`~msl.examples.loadlib.cpp64.Cpp64.reverse_string_v1`:

.. code-block:: python

   >>> cpp.reverse_string_v1('hello world!')
   '!dlrow olleh'

Reverse a string. The memory for the reversed string is allocated in C++,
see :meth:`~msl.examples.loadlib.cpp64.Cpp64.reverse_string_v2`:

.. code-block:: python

   >>> cpp.reverse_string_v2('uncertainty')
   'ytniatrecnu'

Shutdown the server, see :meth:`~msl.loadlib.client64.Client64.shutdown_server32`:

.. code-block:: python

   >>> cpp.shutdown_server32()

.. note::
   When using a subclass of :class:`~msl.loadlib.client64.Client64` in a script, the
   :meth:`~msl.loadlib.client64.Client64.shutdown_server32` method gets called automatically
   when the instance of the subclass is about to be destroyed and therefore you do not have to call
   the :meth:`~msl.loadlib.client64.Client64.shutdown_server32` method to shutdown the server.
