.. _usage:

Load a library
==============

If you are loading a 32-bit library in 32-bit Python, or a 64-bit library in 64-bit Python then you
can directly load the library using :class:`~msl.loadlib.load_library.LoadLibrary`, (by default,
:class:`ctypes.CDLL` is used to load the library)

Import :class:`~msl.loadlib.load_library.LoadLibrary`

.. code:: python

   >>> from msl.loadlib import LoadLibrary

Loading a **C++** library, :ref:`cpp_lib <cpp-lib>`

.. code:: python

   >>> cpp = LoadLibrary('./cpp_lib32')
   >>> cpp
   LoadLibrary object at 0x2e41810; libtype=CDLL; path=D:\examples\cpp_lib32.dll
   >>> cpp.lib
   <CDLL 'D:\examples\cpp_lib32.dll', handle 6f920000 at 0x2e41890>
   >>> cpp.lib.add(1, 2)
   3

Loading a **FORTRAN** library, :ref:`fortran_lib <fortran-lib>`

.. code:: python

   >>> import ctypes
   >>> fortran = LoadLibrary('./fortran_lib32')
   >>> fortran
   LoadLibrary object at 0x2e46eb0; libtype=CDLL; path=D:\examples\fortran_lib32.dll
   >>> fortran.lib
   <CDLL 'D:\examples\fortran_lib32.dll', handle 6f660000 at 0x2e5d470>
   >>> fortran.lib.sum_32bit(ctypes.byref(ctypes.c_int32(-5)), ctypes.byref(ctypes.c_int32(25)))
   20

Loading a **C#** library (a .NET Framework Assembly), :ref:`dotnet_lib <dotnet-lib>`

.. code:: python

   >>> net = LoadLibrary('./dotnet_lib32', 'net')
   >>> net
   LoadLibrary object at 0x2e41cf0; libtype=DotNetContainer; path=D:\examples\dotnet_lib32.dll
   >>> net.assembly
   <System.Reflection.RuntimeAssembly object at 0x03099330>
   >>> net.lib
   <msl.loadlib.load_library.DotNetContainer object at 0x03099C10>
   >>> net.lib.StringManipulation.reverse_string('Hello World!')
   '!dlroW olleH'

Loading a Windows **__stdcall** library

.. code:: python

   >>> kernel = LoadLibrary('C:/Windows/SysWOW64/kernel32.dll', 'windll')
   >>> kernel
   LoadLibrary object at 0x30a2bb0; libtype=WinDLL; path=C:\Windows\SysWOW64\kernel32.dll
   >>> kernel.lib
   <WinDLL 'C:\Windows\SysWOW64\kernel32.dll', handle 76e70000 at 0x2e63570>
   >>> from msl.examples.loadlib.kernel32 import SystemTime
   >>> st = SystemTime()
   >>> ret = kernel.lib.GetLocalTime(ctypes.pointer(st))
   >>> '{}/{}/{} {}:{}:{}'.format(st.wYear, st.wMonth, st.wDay, st.wHour, st.wMinute, st.wSecond)
   '2017/2/27 17:12:19.288'

If you want to load a 32-bit library in 64-bit Python then `inter-process communication
<https://en.wikipedia.org/wiki/Inter-process_communication>`_ is used to communicate with
the 32-bit library. Look at the :ref:`tutorials <tutorials>` for more details on how to subclass
the :class:`~msl.loadlib.server32.Server32` and :class:`~msl.loadlib.client64.Client64` classes.
