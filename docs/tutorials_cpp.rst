.. _loadlib-tutorial-cpp:

==========================================
Load a 32-bit C++ library in 64-bit Python
==========================================

This example shows how to access a 32-bit C++ library from 64-bit Python.
:class:`~msl.examples.loadlib.cpp32.Cpp32` is the 32-bit server and
:class:`~msl.examples.loadlib.cpp64.Cpp64` is the 64-bit client.
The source code of the C++ program is available :ref:`here <cpp-lib>`.

.. note::
   If you have issues running the example please make sure that you have the
   :ref:`prerequisites <loadlib-prerequisites>` installed for your operating system.

.. important::
   By default :mod:`ctypes` expects that a :class:`ctypes.c_int` data type is
   returned from the library call. If the returned value from the library is
   not a :class:`ctypes.c_int` then you must redefine the ctypes
   :ref:`restype <python:ctypes-return-types>` value to be the appropriate
   data type. The :class:`~msl.examples.loadlib.cpp32.Cpp32` class shows
   various examples of redefining the :ref:`restype <python:ctypes-return-types>`
   value.

Create a :class:`~msl.examples.loadlib.cpp64.Cpp64` client to communicate
with the 32-bit :ref:`cpp_lib32 <cpp-lib>` library from 64-bit Python

.. invisible-code-block: pycon

   >>> SKIP_IF_MACOS()

.. code-block:: pycon

   >>> from msl.examples.loadlib import Cpp64
   >>> cpp = Cpp64()

Add two integers, see :meth:`~msl.examples.loadlib.cpp64.Cpp64.add`

.. code-block:: pycon

   >>> cpp.add(3, 14)
   17

Subtract two C++ floating-point numbers, see
:meth:`~msl.examples.loadlib.cpp64.Cpp64.subtract`

.. code-block:: pycon

   >>> cpp.subtract(43.2, 3.2)
   40.0

Add or subtract two C++ double-precision numbers, see
:meth:`~msl.examples.loadlib.cpp64.Cpp64.add_or_subtract`

.. code-block:: pycon

   >>> cpp.add_or_subtract(1.0, 2.0, True)
   3.0
   >>> cpp.add_or_subtract(1.0, 2.0, False)
   -1.0

.. _cpp-array-example:

.. include:: tutorials_cpp_array.rst

.. _cpp-string-example:

.. include:: tutorials_cpp_string.rst

.. _cpp-structs-example:

.. include:: tutorials_cpp_struct.rst

Shutdown the 32-bit server when you are done communicating with the 32-bit library

.. code-block:: pycon

   >>> stdout, stderr = cpp.shutdown_server32()
