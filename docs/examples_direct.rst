Directly load a shared library
==============================

If you are loading a 32-bit library into 32-bit Python, or a 64-bit library
into 64-bit Python then you can directly load the library using
:class:`~msl.loadlib.load_library.LoadLibrary`.

Using a 32-bit Python interpreter load the :ref:`cpp_lib32 <cpp-lib>` library.
By default, :class:`~msl.loadlib.load_library.LoadLibrary` loads a library
using :class:`ctypes.CDLL`.

.. code:: python

   >>> import msl.loadlib
   >>> msl.loadlib.IS_PYTHON_64BIT
   False
   >>> cpp = msl.loadlib.LoadLibrary('./cpp_lib32')
   >>> cpp
   LoadLibrary object at 0x3e9f750; libtype=CDLL; path=D:\examples\cpp_lib32.dll
   >>> cpp.lib
   <CDLL 'D:\examples\cpp_lib32.dll', handle 6f1e0000 at 0x3e92f90>

Call the :ref:`cpp_lib32.add <cpp-lib>` function that calculates the sum of two integers

.. code:: python

   >>> import ctypes
   >>> cpp.lib.add(ctypes.c_int32(1), ctypes.c_int32(2))
   3

Next, load the :ref:`dotnet_lib32 <dotnet-lib>` library, which is a 32-bit C# library for the .NET Framework

.. code:: python

   >>> net = msl.loadlib.LoadLibrary('./dotnet_lib32', 'net')
   >>> net
   LoadLibrary object at 0x43aea30; libtype=DotNetContainer; path=D:\examples\dotnet_lib32.dll
   >>> net.assembly
   <System.Reflection.RuntimeAssembly object at 0x03E23390>
   >>> net.lib
   <msl.loadlib.load_library.DotNetContainer object at 0x065BAB70>

The :ref:`dotnet_lib32 <dotnet-lib>` library contains a module (a C# namespace called **DotNetMSL**),
an instance of the **StringManipulation** class and a reference to the **StaticClass** class

.. code:: python

   >>> for item in dir(net.lib):
   ...     if not item.startswith('_'):
   ...         print(item, type(getattr(net.lib, item)))
   ...
   DotNetMSL <class 'CLR.ModuleObject'>
   StaticClass <class 'System.RuntimeType'>
   StringManipulation <class '.StringManipulation'>

View the static methods in the **StaticClass** class

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


Use the **StringManipulation** class in the :ref:`dotnet_lib32 <dotnet-lib>` library to reverse a string

.. code:: python

   >>> net.lib.StringManipulation.reverse_string('abcdefghijklmnopqrstuvwxyz')
   'zyxwvutsrqponmlkjihgfedcba'

Use the **StaticClass** in the :ref:`dotnet_lib32 <dotnet-lib>` library to add five numbers

.. code:: python

   >>> print(net.lib.StaticClass.GetMethod('add_multiple').Invoke(None, [1, 2, 3, 4, 5]))
   15

For more detailed examples on how to pass variables from Python to :mod:`ctypes`
and `Python for .NET <https://pythonnet.github.io/>`_ view the source code of the
example modules that end in **32** on :ref:`this <mod32bit>` page of the documentation.
