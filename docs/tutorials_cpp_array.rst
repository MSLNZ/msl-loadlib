Arrays
------
Multiply a 1D array by a number, see :meth:`~msl.examples.loadlib.cpp64.Cpp64.scalar_multiply`

.. attention::
   The :meth:`~msl.examples.loadlib.cpp64.Cpp64.scalar_multiply` function takes
   a pointer to an array as an input argument, see :ref:`cpp_lib.h <cpp-lib-header>`.
   One cannot pass pointers from :class:`~msl.loadlib.client64.Client64` to
   :class:`~msl.loadlib.server32.Server32` because a 64-bit process cannot share the
   same memory space as a 32-bit process. All 32-bit pointers must be created (using
   :mod:`ctypes`) in the class that is a subclass of :class:`~msl.loadlib.server32.Server32`
   and only the **value** that is stored at that address can be returned to
   :class:`~msl.loadlib.client64.Client64` for use in the 64-bit program.

.. invisible-code-block: pycon

   >>> SKIP_IF_MACOS()
   >>> from msl.examples.loadlib import Cpp64
   >>> cpp = Cpp64()

.. code-block:: pycon

   >>> a = [float(val) for val in range(10)]
   >>> cpp.scalar_multiply(2.0, a)
   [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0]

If you have a :class:`numpy.ndarray` in 64-bit Python then you cannot pass the
ndarray object to :class:`~msl.loadlib.server32.Server32` because the 32-bit
server would need to load the ndarray in a 32-bit version of numpy (which is
not included by default in the 32-bit server, but could be -- see :ref:`refreeze`
for more details). To simplify the procedure you could convert the ndarray to a
:class:`list` using the :meth:`numpy.ndarray.tolist` method

.. code-block:: pycon

   >>> import numpy as np
   >>> a = np.arange(9.)
   >>> cpp.scalar_multiply(3.1, a.tolist())
   [0.0, 3.1, 6.2, 9.3, 12.4, 15.5, 18.6, 21.7, 24.8]

or you could use the builtin :class:`array.array` class

.. code-block:: pycon

   >>> from array import array
   >>> b = array('d', a.tobytes())
   >>> cpp.scalar_multiply(3.1, b)
   [0.0, 3.1, 6.2, 9.3, 12.4, 15.5, 18.6, 21.7, 24.8]

If you want the returned value from `scalar_multiply` to be a numpy ndarray then use

.. code-block:: pycon

   >>> np.array(cpp.scalar_multiply(3.1, b))
   array([ 0. ,  3.1,  6.2,  9.3, 12.4, 15.5, 18.6, 21.7, 24.8])
