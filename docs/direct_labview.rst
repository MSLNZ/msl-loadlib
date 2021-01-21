.. _direct_labview:

LabVIEW
-------
Load a 64-bit LabVIEW_ library in 64-bit Python (view the
:ref:`LabVIEW source code <labview-lib>`).
*To load the 32-bit version in 32-bit Python use* ``'/labview_lib32.dll'``.
*Also, an appropriate LabVIEW Run-Time Engine must be installed.*
*The LabVIEW example is only valid on Windows.*

.. note::
   A LabVIEW_ library can be built into a DLL using the ``__cdecl`` or
   ``__stdcall`` calling convention. Make sure that you specify the
   appropriate `libtype` when instantiating the
   :class:`~msl.loadlib.load_library.LoadLibrary` class.

.. invisible-code-block: pycon

   >>> SKIP_IF_NOT_WINDOWS() or SKIP_IF_LABVIEW64_NOT_INSTALLED() or SKIP_IF_32BIT()

.. code-block:: pycon

   >>> from msl.loadlib import LoadLibrary
   >>> from msl.examples.loadlib import EXAMPLES_DIR
   >>> labview = LoadLibrary(EXAMPLES_DIR + '/labview_lib64.dll')
   >>> labview
   <LoadLibrary libtype=CDLL path=...labview_lib64.dll>
   >>> labview.lib
   <CDLL '...labview_lib64.dll', handle ... at ...>

Create some data to calculate the mean, variance and standard deviation of

.. code-block:: pycon

   >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9]

Convert `data` to a :mod:`ctypes` array and allocate memory for the returned values

.. code-block:: pycon

   >>> from ctypes import c_double, byref
   >>> x = (c_double * len(data))(*data)
   >>> mean, variance, std = c_double(), c_double(), c_double()

Calculate the sample standard deviation (i.e., the third argument is set to 0)
and variance

.. code-block:: pycon

   >>> ret = labview.lib.stdev(x, len(data), 0, byref(mean), byref(variance), byref(std))
   >>> mean.value
   5.0
   >>> variance.value
   7.5
   >>> std.value
   2.7386127875258306

Calculate the population standard deviation (i.e., the third argument is set to 1)
and variance

.. code-block:: pycon

   >>> ret = labview.lib.stdev(x, len(data), 1, byref(mean), byref(variance), byref(std))
   >>> mean.value
   5.0
   >>> variance.value
   6.666666666666667
   >>> std.value
   2.581988897471611

.. _LabVIEW: https://www.ni.com/en-us/shop/labview.html
