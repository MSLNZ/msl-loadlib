.. _loadlib-tutorial-cpp:

==========================================
Load a 32-bit C++ library in 64-bit Python
==========================================

.. note::
   If you have issues running the example please make sure that you have the
   :ref:`prerequisites <loadlib-prerequisites>` installed.

This example shows how to access a 32-bit C++ library from a module that is run by a
64-bit Python interpreter by using `inter-process communication
<https://en.wikipedia.org/wiki/Inter-process_communication>`_.
:class:`~msl.examples.loadlib.cpp32.Cpp32` is the 32-bit server and
:class:`~msl.examples.loadlib.cpp64.Cpp64` is the 64-bit client. The source
code of the C++ program is available :ref:`here <cpp-lib>`.

.. important::
   By default :mod:`ctypes` expects that a :class:`ctypes.c_int` data type is
   returned from the library call. If the returned value from the library is not a
   :class:`ctypes.c_int` then you **MUST** redefine the ctypes
   :ref:`restype <python:ctypes-return-types>` value to be the appropriate data type.
   The :class:`~msl.examples.loadlib.cpp32.Cpp32` class shows various examples of
   redefining the :ref:`restype <python:ctypes-return-types>` value.

The following shows that the :ref:`cpp_lib32 <cpp-lib>` library
cannot be loaded in a 64-bit Python interpreter

.. code-block:: pycon

   >>> from msl.loadlib import LoadLibrary, IS_PYTHON_64BIT
   >>> from msl.examples.loadlib import EXAMPLES_DIR
   >>> IS_PYTHON_64BIT
   True
   >>> cpp = LoadLibrary(EXAMPLES_DIR + '/cpp_lib32')
   Traceback (most recent call last):
     File "<input>", line 1, in <module>
     File "...\msl\loadlib\load_library.py", line 148, in __init__
       self._lib = ctypes.CDLL(self._path)
     File "...\ctypes\__init__.py", line 348, in __init__
       self._handle = _dlopen(self._name, mode)
   OSError: [WinError 193] %1 is not a valid Win32 application

However, the 64-bit version of the C++ library can be directly loaded in 64-bit Python

.. code-block:: pycon

   >>> cpp64 = LoadLibrary(EXAMPLES_DIR + '/cpp_lib64')
   >>> cpp64
   <LoadLibrary libtype=CDLL path=...\cpp_lib64.dll>
   >>> cpp64.lib.add(3, 14)
   17

Instead, create a :class:`~msl.examples.loadlib.cpp64.Cpp64` client to communicate with the
32-bit :ref:`cpp_lib32 <cpp-lib>` library from 64-bit Python

.. code-block:: pycon

   >>> from msl.examples.loadlib import Cpp64
   >>> cpp = Cpp64()
   >>> cpp
   <Cpp64 lib=cpp_lib32.dll address=127.0.0.1:...>
   >>> cpp.lib32_path
   '...\cpp_lib32.dll'

Add two integers, see :meth:`~msl.examples.loadlib.cpp64.Cpp64.add`

.. code-block:: pycon

   >>> cpp.add(3, 14)
   17

Subtract two C++ floating-point numbers, see :meth:`~msl.examples.loadlib.cpp64.Cpp64.subtract`

.. code-block:: pycon

   >>> cpp.subtract(43.2, 3.2)
   40.0

Add or subtract two C++ double-precision numbers, see :meth:`~msl.examples.loadlib.cpp64.Cpp64.add_or_subtract`

.. code-block:: pycon

   >>> cpp.add_or_subtract(1.1, 2.2, True)
   3.3000000000000003
   >>> cpp.add_or_subtract(1.1, 2.2, False)
   -1.1

.. _cpp-array-example:

Arrays
------

Multiply a 1D array by a number, see :meth:`~msl.examples.loadlib.cpp64.Cpp64.scalar_multiply`

.. attention::
   The :meth:`~msl.examples.loadlib.cpp64.Cpp64.scalar_multiply` function takes a pointer to an array as an input
   argument, see :ref:`cpp_lib.h <cpp-lib-header>`. One cannot pass pointers from :class:`~msl.loadlib.client64.Client64`
   to :class:`~msl.loadlib.server32.Server32` because a 64-bit process cannot share the same memory space as a
   32-bit process. All 32-bit pointers must be created (using :mod:`ctypes`) in the class that is a subclass of
   :class:`~msl.loadlib.server32.Server32` and only the **value** that is stored at that address can be returned to
   :class:`~msl.loadlib.client64.Client64` for use in the 64-bit program.

.. code-block:: pycon

   >>> a = [float(val) for val in range(10)]
   >>> cpp.scalar_multiply(2.0, a)
   [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0]

If you have a numpy ndarray in 64-bit Python then you cannot pass the ndarray object to
:class:`~msl.loadlib.server32.Server32` because the 32-bit server would need to load the ndarray in a 32-bit version
of numpy (which is not bundled with the 32-bit server, but could be bundled if you ran the
:mod:`~msl.loadlib.freeze_server32` module and included a 32-bit version of numpy in the frozen executable).
To simplify the procedure we can convert the ndarray to a Python :class:`list` using the :meth:`numpy.ndarray.tolist`
method

.. code-block:: pycon

   >>> import numpy as np
   >>> a = np.arange(9.)
   >>> cpp.scalar_multiply(3.1, a.tolist())
   [0.0, 3.1, 6.2, 9.3, 12.4, 15.5, 18.6, 21.7, 24.8]

If you want the returned value from `scalar_multiply` to be a numpy ndarray then use

.. code-block:: pycon

   >>> np.array(cpp.scalar_multiply(3.1, a.tolist()))
   array([ 0. ,  3.1,  6.2,  9.3, 12.4, 15.5, 18.6, 21.7, 24.8])

.. _cpp-string-example:

Strings
-------

Reverse a string. The memory for the reversed string is allocated in Python,
see :meth:`~msl.examples.loadlib.cpp64.Cpp64.reverse_string_v1`

.. code-block:: pycon

   >>> cpp.reverse_string_v1('hello world!')
   '!dlrow olleh'

Reverse a string. The memory for the reversed string is allocated in C++,
see :meth:`~msl.examples.loadlib.cpp64.Cpp64.reverse_string_v2`

.. code-block:: pycon

   >>> cpp.reverse_string_v2('uncertainty')
   'ytniatrecnu'

.. _cpp-structs-example:

Structs
-------

It is possible to :mod:`pickle` a :class:`ctypes.Structure` and pass the *struct* object between
:class:`~msl.examples.loadlib.cpp64.Cpp64` and :class:`~msl.examples.loadlib.cpp32.Cpp32` provided
that the *struct* is a **fixed size** in memory (i.e., the *struct* does not contain any pointers).
If the *struct* contains pointers then you must create the *struct* within
:class:`~msl.examples.loadlib.cpp32.Cpp32` and you can only pass the **values** of the *struct* between
:class:`~msl.examples.loadlib.cpp64.Cpp64` and :class:`~msl.examples.loadlib.cpp32.Cpp32`.

.. attention::

   The following will only work if :class:`~msl.examples.loadlib.cpp64.Cpp64` is run using Python 3
   because :class:`~msl.examples.loadlib.cpp32.Cpp32` is running on Python 3 and there are issues
   with :mod:`ctypes` and :mod:`pickle` when mixing Python 2 and Python 3.

The :ref:`cpp_lib32 <cpp-lib>` library contains the following structs

.. code-block:: cpp

    struct Point {
        double x;
        double y;
    };

    struct FourPoints {
        Point points[4];
    };

    struct NPoints {
        int n;
        Point *points;
    };

The :meth:`~msl.examples.loadlib.cpp64.Cpp64.distance_4_points` method uses the
:class:`~msl.examples.loadlib.cpp32.FourPoints` struct to calculate the total distance connecting
4 :class:`~msl.examples.loadlib.cpp32.Point` structs. Since the :class:`~msl.examples.loadlib.cpp32.FourPoints`
struct is a **fixed size** it can be created in 64-bit Python, *pickled* and then *unpickled* in
:class:`~msl.examples.loadlib.cpp32.Cpp32`

.. code-block:: pycon

   >>> from msl.examples.loadlib import FourPoints
   >>> fp = FourPoints((0, 0), (0, 1), (1, 1), (1, 0))
   >>> cpp.distance_4_points(fp)
   4.0

The :meth:`Cpp32.circumference <msl.examples.loadlib.cpp32.Cpp32.circumference>` method uses the
:class:`~msl.examples.loadlib.cpp32.NPoints` struct to calculate the circumference of a circle using
*n* :class:`~msl.examples.loadlib.cpp32.Point` structs. Since the :class:`~msl.examples.loadlib.cpp32.NPoints`
struct is **not a fixed size** it must be created in the
:meth:`Cpp32.circumference <msl.examples.loadlib.cpp32.Cpp32.circumference>` method. The
:meth:`Cpp64.circumference <msl.examples.loadlib.cpp64.Cpp64.circumference>` method takes the values of
the *radius* and *n* as input arguments to pass to the
:meth:`Cpp32.circumference <msl.examples.loadlib.cpp32.Cpp32.circumference>` method.

.. code-block:: pycon

   >>> for i in range(16):
   ...     print(cpp.circumference(0.5, 2**i))
   ...
   0.0
   2.0
   2.82842712474619
   3.061467458920718
   3.121445152258052
   3.1365484905459406
   3.1403311569547543
   3.1412772509327787
   3.141513801144288
   3.1415729403671087
   3.141587725277193
   3.1415914215111314
   3.1415923455699404
   3.141592576584724
   3.1415926343379557
   3.1415926487759718

Shutdown the 32-bit server when you are done communicating with the 32-bit library
(the *stdout* and *stderr* streams from the 32-bit server are returned), see
:meth:`~msl.loadlib.client64.Client64.shutdown_server32`

.. code-block:: pycon

   >>> stdout, stderr = cpp.shutdown_server32()

.. note::
   When using a subclass of :class:`~msl.loadlib.client64.Client64` in a script, the
   :meth:`~msl.loadlib.client64.Client64.shutdown_server32` method gets called automatically
   when the instance of the subclass is about to be destroyed and therefore you do not have to call
   the :meth:`~msl.loadlib.client64.Client64.shutdown_server32` method to shutdown the server.
