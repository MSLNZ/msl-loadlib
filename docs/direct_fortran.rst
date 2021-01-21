.. _direct_fortran:

FORTRAN
-------
Load a 64-bit FORTRAN library in 64-bit Python (view the
:ref:`FORTRAN source code <fortran-lib>`).
*To load the 32-bit version in 32-bit Python use* ``'/fortran_lib32'``.

.. invisible-code-block: pycon

   >>> SKIP_IF_32BIT()

.. code-block:: pycon

   >>> from msl.loadlib import LoadLibrary
   >>> from msl.examples.loadlib import EXAMPLES_DIR
   >>> fortran = LoadLibrary(EXAMPLES_DIR + '/fortran_lib64')
   >>> fortran
   <LoadLibrary libtype=CDLL path=...fortran_lib64.dll>
   >>> fortran.lib
   <CDLL '...fortran_lib64.dll', handle ... at ...>

Call the ``factorial`` function. With a FORTRAN library you must pass values by
reference using :mod:`ctypes`, and, since the returned value is not of type
:class:`ctypes.c_int` we must configure :mod:`ctypes` for a value of type
:class:`ctypes.c_double` to be returned

.. code-block:: pycon

   >>> from ctypes import byref, c_int, c_double
   >>> fortran.lib.factorial.restype = c_double
   >>> fortran.lib.factorial(byref(c_int(37)))
   1.3763753091226343e+43
