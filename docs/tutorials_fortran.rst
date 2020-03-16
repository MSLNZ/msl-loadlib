.. _tutorial_fortran:

==============================================
Load a 32-bit FORTRAN library in 64-bit Python
==============================================

.. note::
   If you have issues running the example please make sure that you have the
   :ref:`prerequisites <loadlib-prerequisites>` installed.

This example shows how to access a 32-bit FORTRAN library from a module that is run by a
64-bit Python interpreter by using `inter-process communication
<https://en.wikipedia.org/wiki/Inter-process_communication>`_.
:class:`~msl.examples.loadlib.fortran32.Fortran32` is the 32-bit server and
:class:`~msl.examples.loadlib.fortran64.Fortran64` is the 64-bit client. The source
code of the FORTRAN program is available :ref:`here <fortran-lib>`.

.. important::
   By default :mod:`ctypes` expects that a :class:`ctypes.c_int` data type is
   returned from the library call. If the returned value from the library is not a
   :class:`ctypes.c_int` then you **MUST** redefine the ctypes
   :ref:`restype <python:ctypes-return-types>` value to be the appropriate data type.
   The :class:`~msl.examples.loadlib.fortran32.Fortran32` class shows various examples
   of redefining the :ref:`restype <python:ctypes-return-types>` value.

The following shows that the :ref:`fortran_lib32 <fortran-lib>` library
cannot be loaded in a 64-bit Python interpreter:

.. code-block:: pycon

   >>> from msl.loadlib import LoadLibrary, IS_PYTHON_64BIT
   >>> from msl.examples.loadlib import EXAMPLES_DIR
   >>> IS_PYTHON_64BIT
   True
   >>> f = LoadLibrary(EXAMPLES_DIR + '/fortran_lib32')
   Traceback (most recent call last):
     File "<input>", line 1, in <module>
     File "D:\msl\loadlib\load_library.py", line 109, in __init__
       self._lib = ctypes.CDLL(self._path)
     File "C:\Miniconda3\lib\ctypes\__init__.py", line 348, in __init__
       self._handle = _dlopen(self._name, mode)
   OSError: [WinError 193] %1 is not a valid Win32 application

However, the 64-bit version of the FORTRAN library can be directly loaded in 64-bit Python:

.. code-block:: pycon

   >>> f64 = LoadLibrary(EXAMPLES_DIR + '/fortran_lib64')
   >>> f64
   <LoadLibrary libtype=CDLL path=...\fortran_lib64.dll>
   >>> from ctypes import byref, c_int8
   >>> f64.lib.sum_8bit(byref(c_int8(-50)), byref(c_int8(110)))
   60

Instead, create a :class:`~msl.examples.loadlib.fortran64.Fortran64` client to communicate with the
32-bit :ref:`fortran_lib32 <fortran-lib>` library:

.. code-block:: pycon

   >>> from msl.examples.loadlib import Fortran64
   >>> f = Fortran64()
   >>> f
   <Fortran64 lib=fortran_lib32.dll address=127.0.0.1:...>
   >>> f.lib32_path
   '...\fortran_lib32.dll'

Add two ``int8`` values, see :meth:`~msl.examples.loadlib.fortran64.Fortran64.sum_8bit`:

.. code-block:: pycon

   >>> f.sum_8bit(-50, 110)
   60

Add two ``int16`` values, see :meth:`~msl.examples.loadlib.fortran64.Fortran64.sum_16bit`:

.. code-block:: pycon

   >>> f.sum_16bit(2**15-1, -1)
   32766

Add two ``int32`` values, see :meth:`~msl.examples.loadlib.fortran64.Fortran64.sum_32bit`:

.. code-block:: pycon

   >>> f.sum_32bit(123456788, 1)
   123456789

Add two ``int64`` values, see :meth:`~msl.examples.loadlib.fortran64.Fortran64.sum_64bit`:

.. code-block:: pycon

   >>> f.sum_64bit(-2**63, 1)
   -9223372036854775807

Multiply two ``float32`` values, see :meth:`~msl.examples.loadlib.fortran64.Fortran64.multiply_float32`:

.. code-block:: pycon

   >>> f.multiply_float32(1e30, 2e3)
   1.9999999889914546e+33

Multiply two ``float64`` values, see :meth:`~msl.examples.loadlib.fortran64.Fortran64.multiply_float64`:

.. code-block:: pycon

   >>> f.multiply_float64(1e30, 2e3)
   2.0000000000000002e+33

Check if a value is positive, see :meth:`~msl.examples.loadlib.fortran64.Fortran64.is_positive`:

.. code-block:: pycon

   >>> f.is_positive(1e-100)
   True
   >>> f.is_positive(-1e-100)
   False

Add or subtract two integers, see :meth:`~msl.examples.loadlib.fortran64.Fortran64.add_or_subtract`:

.. code-block:: pycon

   >>> f.add_or_subtract(1000, 2000, True)
   3000
   >>> f.add_or_subtract(1000, 2000, False)
   -1000

Calculate the n'th factorial, see :meth:`~msl.examples.loadlib.fortran64.Fortran64.factorial`:

.. code-block:: pycon

   >>> f.factorial(0)
   1.0
   >>> f.factorial(127)
   3.012660018457658e+213

Calculate the standard deviation of an list of values, see
:meth:`~msl.examples.loadlib.fortran64.Fortran64.standard_deviation`:

.. code-block:: pycon

   >>> f.standard_deviation([float(val) for val in range(1,10)])
   2.7386127875258306

Compute the Bessel function of the first kind of order 0 at ``x``, see
:meth:`~msl.examples.loadlib.fortran64.Fortran64.besselJ0`:

.. code-block:: pycon

   >>> f.besselJ0(8.6)
   0.014622991278741278

Reverse a string, see :meth:`~msl.examples.loadlib.fortran64.Fortran64.reverse_string`:

.. code-block:: pycon

   >>> f.reverse_string('hello world!')
   '!dlrow olleh'

Add two 1D arrays, see :meth:`~msl.examples.loadlib.fortran64.Fortran64.add_1D_arrays`:

.. code-block:: pycon

   >>> a = [float(val) for val in range(1, 10)]
   >>> b = [0.5*val for val in range(1, 10)]
   >>> a
   [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
   >>> b
   [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
   >>> f.add_1D_arrays(a, b)
   [1.5, 3.0, 4.5, 6.0, 7.5, 9.0, 10.5, 12.0, 13.5]

Multiply two matrices, see :meth:`~msl.examples.loadlib.fortran64.Fortran64.matrix_multiply`:

.. code-block:: pycon

   >>> m1 = [[1, 2, 3], [4, 5, 6]]
   >>> m2 = [[1, 2], [3, 4], [5, 6]]
   >>> f.matrix_multiply(m1, m2)
   [[22.0, 28.0], [49.0, 64.0]]

Shutdown the server, see :meth:`~msl.loadlib.client64.Client64.shutdown_server32`:

.. code-block:: pycon

   >>> f.shutdown_server32()

.. note::
   When using a subclass of :class:`~msl.loadlib.client64.Client64` in a script, the
   :meth:`~msl.loadlib.client64.Client64.shutdown_server32` method gets called automatically
   when the instance of the subclass is about to be destroyed and therefore you do not have to call
   the :meth:`~msl.loadlib.client64.Client64.shutdown_server32` method to shutdown the server.
