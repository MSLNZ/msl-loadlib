.. _direct:

Load a library
==============

If you are loading a 32-bit library in to 32-bit Python, or a 64-bit library in to 64-bit Python
then you can directly load the library using :class:`~msl.loadlib.load_library.LoadLibrary`.

.. note::
   All of the shared libraries in the examples are included with the **MSL-LoadLib** package.

The :ref:`C++ <cpp-lib>` and :ref:`FORTRAN <fortran-lib>` libraries have been compiled in 32-
and 64-bit Windows and Linux. The :ref:`.NET <dotnet-lib>` library was complied to 32 and 64 bit
using Microsoft Visual Studio. The
`kernel32 <http://www.geoffchappell.com/studies/windows/win32/kernel32/api/>`_ library is only
valid on Windows, since it uses the ``__stdcall`` calling convention. The :ref:`LabVIEW <labview-lib>`
library was built using 64-bit LabVIEW on Windows. The :ref:`Java <java-lib>` archive is platform
and bitness independent since it runs in the JVM_.

.. important::
   If you want to load a 32-bit library in 64-bit Python then `inter-process communication
   <https://en.wikipedia.org/wiki/Inter-process_communication>`_ is used to communicate with
   the 32-bit library. See the :ref:`examples <inter-process-communication>` for more details.

The first step is to import the :class:`~msl.loadlib.load_library.LoadLibrary` class

.. code:: python

   >>> from msl.loadlib import LoadLibrary

and the directory where the example libraries are located

.. code:: python

   >>> from msl.examples.loadlib import EXAMPLES_DIR

C++
---
Loading a 64-bit **C++** library in 64-bit Python, see :ref:`here <cpp-lib>` for the source code.
*To load the 32-bit version in 32-bit Python use* ``'cpp_lib32'``.

.. code:: python

   >>> cpp = LoadLibrary(EXAMPLES_DIR + '/cpp_lib64')
   >>> cpp
   <LoadLibrary id=0x2e41810 libtype=CDLL path=D:\msl\examples\loadlib\cpp_lib64.dll>
   >>> cpp.lib
   <CDLL 'D:\msl\examples\loadlib\cpp_lib64.dll', handle 6f920000 at 0x3e92f90>

Call the ``add`` function that calculates the sum of two integers

.. code:: python

   >>> cpp.lib.add(1, 2)
   3

FORTRAN
-------
Loading a 64-bit **FORTRAN** library in 64-bit Python, see :ref:`here <fortran-lib>` for the source code.
*To load the 32-bit version in 32-bit Python use* ``'fortran_lib32'``.

.. code:: python

   >>> fortran = LoadLibrary(EXAMPLES_DIR + '/fortran_lib64')
   >>> fortran
   <LoadLibrary id=0x2e46eb0 libtype=CDLL path=D:\msl\examples\loadlib\fortran_lib64.dll>
   >>> fortran.lib
   <CDLL 'D:\msl\examples\loadlib\fortran_lib64.dll', handle 6f660000 at 0x2e5d470>

Call the ``sum_8bit`` function that calculates the sum of two 8-bit integers. For **FORTRAN**
you must pass the value by reference

.. code:: python

   >>> from ctypes import c_int8, byref
   >>> fortran.lib.sum_8bit.restype = c_int8
   >>> fortran.lib.sum_8bit(byref(c_int8(-5)), byref(c_int8(25)))
   20

Microsoft .NET
--------------
Load a 64-bit **C#** library (a .NET Framework library) in 64-bit Python, see :ref:`here <dotnet-lib>`
for the source code. *To load the 32-bit version in 32-bit Python use* ``'dotnet_lib32.dll'``.

.. code:: python

   >>> net = LoadLibrary(EXAMPLES_DIR + '/dotnet_lib64.dll', 'net')
   >>> net
   <LoadLibrary id=0x2e41cf0 libtype=DotNet path=D:\msl\examples\loadlib\dotnet_lib64.dll>
   >>> net.assembly
   <System.Reflection.RuntimeAssembly object at 0x03099330>
   >>> net.lib
   <DotNet id=0x03099C10 path=D:\msl\examples\loadlib\dotnet_lib64.dll>

The :ref:`dotnet_lib64 <dotnet-lib>` library contains a reference to the ``DotNetMSL`` module
(which is a C# namespace), an instance of the ``StringManipulation`` class and a reference to the
``StaticClass`` class

.. code:: python

   >>> for item in dir(net.lib):
   ...     if not item.startswith('_'):
   ...         print(item, type(getattr(net.lib, item)))
   ...
   DotNetMSL <class 'CLR.ModuleObject'>
   StaticClass <class 'System.RuntimeType'>
   StringManipulation <class '.StringManipulation'>

View the static methods in the ``StaticClass`` class

.. code:: python

   >>> for method in net.lib.StaticClass.GetMethods():
   ...     print(method)
   ...
   Int32 add_multiple(Int32, Int32, Int32, Int32, Int32)
   System.String concatenate(System.String, System.String, System.String, Boolean, System.String)
   System.String ToString()
   Boolean Equals(System.Object)
   Int32 GetHashCode()
   System.Type GetType()

Use the ``reverse_string`` method in the ``StringManipulation`` class in the :ref:`dotnet_lib64 <dotnet-lib>`
library to reverse a string

.. code:: python

   >>> net.lib.StringManipulation.reverse_string('abcdefghijklmnopqrstuvwxyz')
   'zyxwvutsrqponmlkjihgfedcba'

Use the static ``add_multiple`` method in the ``StaticClass`` class in the :ref:`dotnet_lib64 <dotnet-lib>`
library to add five integers

.. code:: python

   >>> net.lib.StaticClass.GetMethod('add_multiple').Invoke(None, [1, 2, 3, 4, 5])
   15

Windows __stdcall
-----------------
Load a 32-bit Windows **__stdcall** library in 32-bit Python, see
`kernel32.dll <http://www.geoffchappell.com/studies/windows/win32/kernel32/api/>`_

.. code:: python

   >>> kernel = LoadLibrary('C:/Windows/SysWOW64/kernel32.dll', 'windll')
   >>> kernel
   <LoadLibrary id=0x30a2bb0 libtype=WinDLL path=C:\Windows\SysWOW64\kernel32.dll>
   >>> kernel.lib
   <WinDLL 'C:\Windows\SysWOW64\kernel32.dll', handle 76e70000 at 0x2e63570>
   >>> from msl.examples.loadlib.kernel32 import SystemTime
   >>> st = SystemTime()
   >>> from ctypes import pointer
   >>> ret = kernel.lib.GetLocalTime(pointer(st))
   >>> '{}-{}-{} {}:{}:{}'.format(st.wYear, st.wMonth, st.wDay, st.wHour, st.wMinute, st.wSecond)
   '2017-2-27 17:12:19.288'

See :ref:`here <tutorial_stdcall>` for how to communicate with ``kernel32.dll`` from 64-bit Python.

LabVIEW
-------
Load a 64-bit **LabVIEW** library in 64-bit Python, see :ref:`here <labview-lib>` for the source code.
*Note: A 32-bit version of the LabVIEW library is not included with the MSL-LoadLib package.*

.. code:: python

   >>> labview = LoadLibrary(EXAMPLES_DIR + '/labview_lib64.dll')
   >>> labview
   <LoadLibrary id=0x2060085bd68 libtype=CDLL path=D:\msl\examples\loadlib\labview_lib64.dll>

Create some data to calculate the mean, variance and standard deviation

.. code:: python

   >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9]

convert it to :mod:`ctypes`

.. code:: python

   >>> from ctypes import c_double, byref
   >>> x = (c_double * len(data))(*data)
   >>> mean, variance, stdev = c_double(), c_double(), c_double()

calculate the *sample* standard deviation (the third argument is set to 0)

.. code:: python

   >>> ret = labview.lib.stdev(x, len(data), 0, byref(mean), byref(variance), byref(stdev))
   >>> mean.value
   5.0
   >>> variance.value
   7.5
   >>> stdev.value
   2.7386127875258306

calculate the *population* standard deviation (the third argument is set to 1)

.. code:: python

   >>> ret = labview.lib.stdev(x, len(data), 1, byref(mean), byref(variance), byref(stdev))
   >>> mean.value
   5.0
   >>> variance.value
   6.666666666666667
   >>> stdev.value
   2.581988897471611

Java
----
Since Java byte code is executed in the JVM_ it doesn't matter whether it was built with a 32-bit or
64-bit Java Development Kit. The Python interpreter does not load the Java byte code but communicates
with the JVM_ through a local network socket that is created by `Py4J <https://www.py4j.org/>`_.

Load a **Java** archive, a ``JAR`` file, in a JVM_, see :ref:`here <java-lib>` for the source code.

.. code:: python

   >>> jar = LoadLibrary(EXAMPLES_DIR + '/java_lib.jar')
   >>> jar
   <LoadLibrary id=0x206008993c8 libtype=JVMView path=D:\msl\examples\loadlib\java_lib.jar>
   >>> jar.gateway
   <py4j.java_gateway.JavaGateway object at 0x000002061A4524E0>

The Java archive contains a ``nz.msl.example`` package with two classes, ``MathUtils`` and ``Matrix``

.. code:: python

   >>> MathUtils = jar.lib.nz.msl.example.MathUtils
   >>> Matrix = jar.lib.nz.msl.example.Matrix

Generate a random number and calculate the square root of a number using the ``MathUtils`` class

.. code:: python

   >>> MathUtils.random()
   0.17555846754602522
   >>> MathUtils.sqrt(32.4)
   5.692099788303083

Use the ``Matrix`` class to calculate the inverse of a 3x3 matrix that is filled with random
numbers between 0 and 100

.. code:: python

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

.. code:: python

   >>> A = jar.gateway.new_array(jar.lib.Double, 3, 3)
   >>> coeff = [[3, 2, -1], [7, -2, 4], [-1, 5, 1]]
   >>> for i in range(3):
   ...     for j in range(3):
   ...         A[i][j] = float(coeff[i][j])
   >>> b = jar.gateway.new_array(jar.lib.Double, 3)
   >>> b[0] = 1.6
   >>> b[1] = -12.3
   >>> b[2] = 3.4
   >>> x = Matrix.solve(Matrix(A), Matrix(b))
   >>> print(x.toString())
   -5.892562e-01
   +8.826446e-01
   -1.602479e+00
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

.. code:: python

   >>> jar.gateway.shutdown()

.. _JVM: https://en.wikipedia.org/wiki/Java_virtual_machine
