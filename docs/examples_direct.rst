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
   LoadLibrary object at 0x3e9f750; libtype=ctypes.CDLL; path=D:\examples\cpp_lib32.dll
   >>> cpp.lib
   <CDLL 'D:\examples\cpp_lib32.dll', handle 6f1e0000 at 0x3e92f90>

Call the :ref:`cpp_lib32.add <cpp-lib>` function that calculates the sum of two integers

.. code:: python

   >>> import ctypes
   >>> cpp.lib.add(ctypes.c_int32(1), ctypes.c_int32(2))
   3

Next, load the **dotnet_lib32.dll** library, which is a 32-bit .NET Framework library. The
**dotnet_lib32.dll** file is a library for the `EPSON RC+ 6-axis robot
<http://www.d.umn.edu/~rlindek1/ME4135_11/e_SPEL%2BRef54_r1.pdf>`_, ``SpelNetLib``.

.. code:: python

   >>> dot = msl.loadlib.LoadLibrary('./dotnet_lib32', 'net')
   >>> dot
   LoadLibrary object at 0x37c27b0; libtype=CLR.ModuleObject; path=D:\examples\dotnet_lib32.dll
   >>> dot.net
   <System.Reflection.RuntimeAssembly object at 0x03E23390>
   >>> dot.lib
   <module 'SpelNetLib'>

Display the classes that are available in the ``SpelNetLib`` module

.. code:: python

   >>> for cls in dot.net.GetExportedTypes():
   ...     print(cls)
   ...
   SpelNetLib.SPELVideo
   SpelNetLib.SpelControllerInfo
   SpelNetLib.SpelEventArgs
   SpelNetLib.SpelPoint
   SpelNetLib.Spel
   SpelNetLib.Spel+EventReceivedEventHandler
   SpelNetLib.SpelException
   SpelNetLib.SpelAxis
   SpelNetLib.SpelBaseAlignment
   SpelNetLib.SpelDialogs
   SpelNetLib.SpelIOLabelTypes
   SpelNetLib.SpelWindows
   SpelNetLib.SpelEvents
   SpelNetLib.SpelHand
   SpelNetLib.SpelElbow
   SpelNetLib.SpelOperationMode
   SpelNetLib.SpelRobotPosType
   SpelNetLib.SpelRobotType
   SpelNetLib.SpelTaskState
   SpelNetLib.SpelTaskType
   SpelNetLib.SpelWrist
   SpelNetLib.SpelVisionProps

For more detailed examples on how to pass variables from Python to :mod:`ctypes`
and `Python for .NET <https://pythonnet.github.io/>`_ view the source code of the
example modules that end in **32** on :ref:`this <mod32bit>` page of the documentation.
