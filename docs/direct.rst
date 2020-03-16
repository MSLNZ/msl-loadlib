.. _direct:

Load a library
==============

If you are loading a 32-bit library in 32-bit Python, or a 64-bit library in 64-bit Python,
then you can directly load the library using :class:`~msl.loadlib.load_library.LoadLibrary`.

.. important::
   If you want to load a 32-bit library in 64-bit Python then `inter-process communication
   <https://en.wikipedia.org/wiki/Inter-process_communication>`_ is used to communicate with
   the 32-bit library. See the :ref:`examples <inter-process-communication>` for more details.

All of the shared libraries in the following examples are included with the **MSL-LoadLib** package.
The :ref:`C++ <cpp-lib>` and :ref:`FORTRAN <fortran-lib>` libraries have been compiled in 32-
and 64-bit Windows and Linux, using *g++* and *gfortran* respectively. The :ref:`.NET <dotnet-lib>`
library was complied to 32 and 64 bit using Microsoft Visual Studio. The
`kernel32 <https://www.geoffchappell.com/studies/windows/win32/kernel32/api/>`_ library is a 32-bit
library and it is only valid on Windows, since it uses the ``__stdcall`` calling convention.
The :ref:`LabVIEW <labview-lib>` library was built using 32- and 64-bit LabVIEW on Windows.
The :ref:`Java <java-lib>` libraries are platform and bitness independent since they run in the JVM_.

The first step is to import the :class:`~msl.loadlib.load_library.LoadLibrary` class

.. code-block:: pycon

   >>> from msl.loadlib import LoadLibrary

and the directory where the example libraries are located

.. code-block:: pycon

   >>> from msl.examples.loadlib import EXAMPLES_DIR

.. tip::
   If the file extension is not specified then a default extension, ``.dll`` (Windows), ``.so`` (Linux)
   or ``.dylib`` (macOS) is used.

C++
---
Load a 64-bit C++ library in 64-bit Python, see :ref:`here <cpp-lib>` for the source code.
*To load the 32-bit version in 32-bit Python use* ``'cpp_lib32'``.

.. code-block:: pycon

   >>> cpp = LoadLibrary(EXAMPLES_DIR + '/cpp_lib64')
   >>> cpp
   <LoadLibrary libtype=CDLL path=...\cpp_lib64.dll>
   >>> cpp.lib
   <CDLL '...\cpp_lib64.dll', handle ... at ...>

Call the ``add`` function that calculates the sum of two integers

.. code-block:: pycon

   >>> cpp.lib.add(1, 2)
   3

FORTRAN
-------
Load a 64-bit FORTRAN library in 64-bit Python, see :ref:`here <fortran-lib>` for the source code.
*To load the 32-bit version in 32-bit Python use* ``'fortran_lib32'``.

.. code-block:: pycon

   >>> fortran = LoadLibrary(EXAMPLES_DIR + '/fortran_lib64')
   >>> fortran
   <LoadLibrary libtype=CDLL path=...\fortran_lib64.dll>
   >>> fortran.lib
   <CDLL '...\fortran_lib64.dll', handle ... at ...>

Call the ``factorial`` function. With a FORTRAN library you must pass values by reference using :mod:`ctypes`,
and, since the returned value is not of type :class:`ctypes.c_int` we must configure :mod:`ctypes` for a value
of type :class:`ctypes.c_double` to be returned

.. code-block:: pycon

   >>> from ctypes import byref, c_int, c_double
   >>> fortran.lib.factorial.restype = c_double
   >>> fortran.lib.factorial(byref(c_int(37)))
   1.3763753091226343e+43

Microsoft .NET Framework
------------------------
Load a 64-bit C# library (a .NET Framework) in 64-bit Python, see :ref:`here <dotnet-lib>`
for the source code. Include the ``'net'`` argument to indicate that the ``.dll`` file is for
the .NET Framework (``'clr'`` is an alias for ``'net'`` and can be used as the `libtype`).
*To load the 32-bit version in 32-bit Python use* ``'dotnet_lib32.dll'``.

.. code-block:: pycon

   >>> net = LoadLibrary(EXAMPLES_DIR + '/dotnet_lib64.dll', 'net')
   >>> net
   <LoadLibrary libtype=DotNet path=...\dotnet_lib64.dll>
   >>> net.assembly
   <System.Reflection.RuntimeAssembly object at ...>
   >>> net.lib
   <DotNet path=...\dotnet_lib64.dll>

The :ref:`dotnet_lib64 <dotnet-lib>` library contains a reference to the ``DotNetMSL`` module
(which is a C# namespace), an instance of the ``StringManipulation`` class and a reference to the
``StaticClass`` class

.. code-block:: pycon

   >>> for item in dir(net.lib):
   ...     if not item.startswith('_'):
   ...         print(item, type(getattr(net.lib, item)))
   ...
   DotNetMSL <class 'CLR.ModuleObject'>
   StaticClass <class 'CLR.CLR Metatype'>
   StringManipulation <class 'CLR.CLR Metatype'>
   System <class 'CLR.ModuleObject'>

Create an instance of the ``BasicMath`` class in the ``DotNetMSL`` namespace and call the
``multiply_doubles`` method

.. code-block:: pycon

   >>> bm = net.lib.DotNetMSL.BasicMath()
   >>> bm.multiply_doubles(2.3, 5.6)
   12.879999999999999

Create an instance of the ``ArrayManipulation`` class in the ``DotNetMSL`` namespace and call the
``scalar_multiply`` method

.. code-block:: pycon

   >>> am = net.lib.DotNetMSL.ArrayManipulation()
   >>> values = am.scalar_multiply(2., [1., 2., 3., 4., 5.])
   >>> values
   <System.Double[] object at ...>
   >>> [val for val in values]
   [2.0, 4.0, 6.0, 8.0, 10.0]

Use the ``reverse_string`` method in the ``StringManipulation`` class to reverse a string

.. code-block:: pycon

   >>> net.lib.StringManipulation().reverse_string('abcdefghijklmnopqrstuvwxyz')
   'zyxwvutsrqponmlkjihgfedcba'

Use the static ``add_multiple`` method in the ``StaticClass`` class to add five integers

.. code-block:: pycon

   >>> net.lib.StaticClass.add_multiple(1, 2, 3, 4, 5)
   15

Windows __stdcall
-----------------
Load a 32-bit Windows ``__stdcall`` library in 32-bit Python, see
`kernel32.dll <https://www.geoffchappell.com/studies/windows/win32/kernel32/api/>`_. Include the
``'windll'`` argument to specify that the calling convention is ``__stdcall``.

.. code-block:: pycon

   >>> kernel = LoadLibrary('C:/Windows/SysWOW64/kernel32.dll', 'windll')
   >>> kernel
   <LoadLibrary libtype=WinDLL path=C:\Windows\SysWOW64\kernel32.dll>
   >>> kernel.lib
   <WinDLL 'C:\Windows\SysWOW64\kernel32.dll', handle ... at ...>
   >>> from msl.examples.loadlib.kernel32 import SystemTime
   >>> st = SystemTime()
   >>> from ctypes import pointer
   >>> ret = kernel.lib.GetLocalTime(pointer(st))
   >>> '{}-{}-{} {}:{}:{}'.format(st.wYear, st.wMonth, st.wDay, st.wHour, st.wMinute, st.wSecond)
   '2017-2-27 17:12:19'

See :ref:`here <tutorial_stdcall>` for how to communicate with ``kernel32.dll`` from 64-bit Python.

LabVIEW
-------
Load a 64-bit LabVIEW library in 64-bit Python, see :ref:`here <labview-lib>` for the source code.
*To load the 32-bit version in 32-bit Python use* ``'labview_lib32.dll'``. *Also, an appropriate LabVIEW*
*Run-Time Engine must be installed. The LabVIEW example is only valid on Windows.*

.. note::
   A LabVIEW library can be built into a DLL using the ``__cdecl`` or  ``__stdcall`` calling convention.
   Make sure that you specify the appropriate `libtype` when instantiating the
   :class:`~msl.loadlib.load_library.LoadLibrary` class.

.. code-block:: pycon

   >>> labview = LoadLibrary(EXAMPLES_DIR + '/labview_lib64.dll')
   >>> labview
   <LoadLibrary libtype=CDLL path=...\labview_lib64.dll>
   >>> labview.lib
   <CDLL '...\labview_lib64.dll', handle ... at ...>

Create some data to calculate the mean, variance and standard deviation of

.. code-block:: pycon

   >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9]

Convert `data` to a :mod:`ctypes` array and allocate memory for the returned values

.. code-block:: pycon

   >>> from ctypes import c_double, byref
   >>> x = (c_double * len(data))(*data)
   >>> mean, variance, std = c_double(), c_double(), c_double()

Calculate the sample standard deviation (i.e., the third argument is set to 0) and variance

.. code-block:: pycon

   >>> ret = labview.lib.stdev(x, len(data), 0, byref(mean), byref(variance), byref(std))
   >>> mean.value
   5.0
   >>> variance.value
   7.5
   >>> std.value
   2.7386127875258306

Calculate the population standard deviation (i.e., the third argument is set to 1) and variance

.. code-block:: pycon

   >>> ret = labview.lib.stdev(x, len(data), 1, byref(mean), byref(variance), byref(std))
   >>> mean.value
   5.0
   >>> variance.value
   6.666666666666667
   >>> std.value
   2.581988897471611

Java
----
Since Java byte code is executed in the JVM_ it doesn't matter whether it was built with a 32-bit or
64-bit Java Development Kit. The Python interpreter does not load the Java byte code but communicates
with the JVM_ through a local network socket that is created by `Py4J <https://www.py4j.org/>`_.

Load a Java archive, a ``.jar`` file, in a JVM_, see :ref:`here <java-lib-jar>` for the source code.

.. code-block:: pycon

   >>> jar = LoadLibrary(EXAMPLES_DIR + '/java_lib.jar')
   >>> jar
   <LoadLibrary libtype=JVMView path=...\java_lib.jar>
   >>> jar.gateway
   <py4j.java_gateway.JavaGateway object at ...>

The Java archive contains a ``nz.msl.examples`` package with two classes, ``MathUtils`` and ``Matrix``

.. code-block:: pycon

   >>> MathUtils = jar.lib.nz.msl.examples.MathUtils
   >>> Matrix = jar.lib.nz.msl.examples.Matrix

Generate a random number and calculate the square root of a number using the ``MathUtils`` class

.. code-block:: pycon

   >>> MathUtils.random()
   0.17555846754602522
   >>> MathUtils.sqrt(32.4)
   5.692099788303083

Use the ``Matrix`` class to calculate the inverse of a 3x3 matrix that is filled with random
numbers between 0 and 100

.. code-block:: pycon

   >>> m = Matrix(3, 3, 0.0, 100.0)
   >>> print(m.toString())
   +5.937661e+01  +5.694407e+01  +5.132319e+01
   +2.443462e+01  +9.051636e+00  +5.500980e+01
   +6.183735e+01  +9.492954e+01  +4.519221e+01
   >>> m_inverse = m.getInverse()
   >>> print(m_inverse.toString())
   +7.446422e-02  -3.556370e-02  -4.127679e-02
   -3.554433e-02  +7.586144e-03  +3.113227e-02
   -2.722735e-02  +3.272723e-02  +1.321192e-02
   >>> identity = Matrix.multiply(m, m_inverse)
   >>> print(identity.toString())
   +1.000000e+00  +0.000000e+00  +2.220446e-16
   +0.000000e+00  +1.000000e+00  +1.110223e-16
   +0.000000e+00  -4.440892e-16  +1.000000e+00

Solve a linear system of equations, Ax=b

.. code-block:: pycon

   >>> A = jar.gateway.new_array(jar.lib.Double, 3, 3)
   >>> coeff = [[3, 2, -1], [7, -2, 4], [-1, 5, 1]]
   >>> for i in range(3):
   ...     for j in range(3):
   ...         A[i][j] = float(coeff[i][j])
   ...
   >>> b = jar.gateway.new_array(jar.lib.Double, 3)
   >>> b[0] = 1.6
   >>> b[1] = -12.3
   >>> b[2] = 3.4
   >>> x = Matrix.solve(Matrix(A), Matrix(b))
   >>> print(x.toString())
   -5.892562e-01
   +8.826446e-01
   -1.602479e+00

Show that `x` is a solution by getting `b` back

.. code-block:: pycon

   >>> for i in range(3):
   ...     val = 0.0
   ...     for j in range(3):
   ...         val += coeff[i][j]*x.getValue(j,0)
   ...     print(val)
   ...
   1.5999999999999999
   -12.3
   3.4000000000000012

Shutdown the connection to the JVM_ when you are finished

.. code-block:: pycon

   >>> jar.gateway.shutdown()

Load Java byte code, a ``.class`` file, in a JVM_, see :ref:`here <java-lib-class>` for the source code.

.. code-block:: pycon

   >>> cls = LoadLibrary(EXAMPLES_DIR + '/Trig.class')
   >>> cls
   <LoadLibrary libtype=JVMView path=...\Trig.class>
   >>> cls.lib
   <py4j.java_gateway.JVMView object at ...>

The Java library contains a ``Trig`` class, which calculates various trigonometric quantities

.. code-block:: pycon

   >>> Trig = cls.lib.Trig
   >>> Trig
   <py4j.java_gateway.JavaClass object at ...>
   >>> Trig.cos(1.2)
   0.3623577544766736
   >>> Trig.asin(0.6)
   0.6435011087932844
   >>> Trig.tanh(1.3)
   0.8617231593133063

Once again, shutdown the connection to the JVM_ when you are finished

.. code-block:: pycon

   >>> cls.gateway.shutdown()

COM
---
To load a `Component Object Model`_ (COM) library pass in the library's Program ID.
To view the COM libraries that are available on your computer you can run the
:func:`~msl.loadlib.utils.get_com_info` function.

.. attention::

   This example will only work on Windows.

Here we load the FileSystemObject_ library and include the ``'com'`` argument to indicate that
it is a COM library

.. code-block:: pycon

   >>> com = LoadLibrary('Scripting.FileSystemObject', 'com')
   >>> com
   <LoadLibrary libtype=POINTER(IFileSystem3) path=Scripting.FileSystemObject>

We can then use the library to create, edit and close a text file

.. code-block:: pycon

   >>> fp = com.lib.CreateTextFile('a_new_file.txt')
   >>> fp.WriteLine('This is a test')
   0
   >>> fp.Close()
   0

.. tip::

   If you are loading a COM library and you get the following error

   .. code-block:: console

      OSError: [WinError -2147417850] Cannot change thread mode after it is set

   then you can remove this error by setting ``sys.coinit_flags = 0`` before
   loading the library

   For example,

   .. code-block:: python

      import sys
      sys.coinit_flags = 0
      com = LoadLibrary('Scripting.FileSystemObject', 'com')


.. _JVM: https://en.wikipedia.org/wiki/Java_virtual_machine
.. _FileSystemObject: https://docs.microsoft.com/en-us/office/vba/language/reference/user-interface-help/filesystemobject-object
.. _Component Object Model: https://en.wikipedia.org/wiki/Component_Object_Model
