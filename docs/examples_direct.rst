Directly load a shared library
==============================

If you are loading a 32-bit library in to 32-bit Python, or a 64-bit library
in to 64-bit Python then you can directly load the library using
:class:`~msl.loadlib.load_library.LoadLibrary`.

Using a 64-bit Python interpreter load the :ref:`cpp_lib64 <cpp-lib>` library.
By default, :class:`~msl.loadlib.load_library.LoadLibrary` loads a library
using :class:`ctypes.CDLL`.

.. code:: python

   >>> from msl import loadlib
   >>> from msl.examples.loadlib import EXAMPLES_DIR
   >>> loadlib.IS_PYTHON_64BIT
   True
   >>> cpp = loadlib.LoadLibrary(EXAMPLES_DIR + '/cpp_lib64')
   >>> cpp
   <LoadLibrary id=0x394bba8 libtype=CDLL path=D:\msl\examples\loadlib\cpp_lib64.dll>
   >>> cpp.lib
   <CDLL 'D:\msl\examples\loadlib\cpp_lib64.dll', handle 6f1e0000 at 0x3e92f90>

Call the :ref:`cpp_lib64.add <cpp-lib>` function that calculates the sum of two integers

.. code:: python

   >>> cpp.lib.add(1, 2)
   3

Next, load the :ref:`dotnet_lib64 <dotnet-lib>` library, which is a 64-bit C# library for the .NET Framework

.. code:: python

   >>> net = loadlib.LoadLibrary(EXAMPLES_DIR + '/dotnet_lib64', 'net')
   >>> net
   <LoadLibrary id=0x396f668 libtype=DotNet path=D:\msl\examples\loadlib\dotnet_lib64.dll>
   >>> net.assembly
   <System.Reflection.RuntimeAssembly object at 0x03E23390>
   >>> net.lib
   <DotNet id=0x3d08550 path=D:\msl\examples\loadlib\dotnet_lib64.dll>

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

For more detailed examples on how to pass variables from Python to :mod:`ctypes`
and `Python for .NET <https://pythonnet.github.io/>`_ view the source code of the
example modules that end in ``32`` on :ref:`this <mod32bit>` page of the documentation.
