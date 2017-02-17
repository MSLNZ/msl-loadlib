.. _usage:

Load a library
==============

If you are loading a 32-bit library in 32-bit Python, or a 64-bit library
in 64-bit Python then you can directly load the library using
:class:`~msl.loadlib.load_library.LoadLibrary`, (by default, :class:`ctypes.CDLL`
is used to load the library)

.. code:: python

   >>> from msl.loadlib import LoadLibrary
   >>> a = LoadLibrary('./cpp_lib32')
   >>> a
   LoadLibrary object at 0x195cd0; libtype=ctypes.CDLL; path=D:\examples\cpp_lib32.dll
   >>> a.lib
   <CDLL 'D:\examples\cpp_lib32.dll', handle 52cb0000 at 0x4b5d30>
   >>> b = LoadLibrary('./dotnet_lib32', 'net')
   >>> b
   LoadLibrary object at 0x2a5cd0; libtype=CLR.ModuleObject; path=D:\examples\dotnet_lib32.dll
   >>> b.lib
   <module 'SpelNetLib'>
   >>> c = LoadLibrary('C:/Windows/SysWOW64/kernel32.dll', 'windll')
   >>> c
   LoadLibrary object at 0x595d30; libtype=ctypes.WinDLL; path=C:\Windows\SysWOW64\kernel32.dll
   >>> c.lib
   <WinDLL 'C:\Windows\SysWOW64\kernel32.dll', handle 74f10000 at 0xa7e8d0>
   >>> d = LoadLibrary('./fortran_lib32')
   >>> d
   LoadLibrary object at 0x5e5cd0; libtype=ctypes.CDLL; path=D:\examples\fortran_lib32.dll
   >>> d.lib
   <CDLL 'D:\examples\fortran_lib32.dll', handle f860000 at 0x5e5d30>

If you want to load a 32-bit library in 64-bit Python then `inter-process communication
<https://en.wikipedia.org/wiki/Inter-process_communication>`_ is used to communicate with
the 32-bit library. Look at the :ref:`tutorials <tutorials>` for more details on how to subclass
the :class:`~msl.loadlib.server32.Server32` and :class:`~msl.loadlib.client64.Client64` classes.
