.. _api:

=============================
MSL-LoadLib API Documentation
=============================

The root package is

.. autosummary::

    msl.loadlib

which has the following class for directly loading a shared library,

+-----------------------------------------+------------------------------------------------------------------+
| :class:`msl.loadlib.LoadLibrary         | Load a :class:`~ctypes.CDLL`, :class:`~ctypes.WinDLL`,           |
| <msl.loadlib.load_library.LoadLibrary>` | :class:`~ctypes.OleDLL`, or a                                    |
|                                         | `.NET Framework <http://pythonnet.github.io/>`_  shared library. |
+-----------------------------------------+------------------------------------------------------------------+

the following client-server classes for communicating with a 32-bit library from 64-bit Python,

+----------------------------------+-------------------------------------------------------------------+
| :class:`msl.loadlib.Client64     | Base class for communicating with a 32-bit shared library from    |
| <msl.loadlib.client64.Client64>` | 64-bit Python.                                                    |
+----------------------------------+-------------------------------------------------------------------+
| :class:`msl.loadlib.Server32     | Base class for loading a 32-bit shared library in 32-bit Python.  |
| <msl.loadlib.server32.Server32>` |                                                                   |
+----------------------------------+-------------------------------------------------------------------+

and the following modules for creating a `frozen <http://www.pyinstaller.org/>`_
32-bit server for hosting a 32-bit library

.. autosummary::

   msl.loadlib.freeze_server32
   msl.loadlib.start_server32


Package Structure
-----------------

.. toctree::

   msl.loadlib <_api/msl.loadlib>
   msl.loadlib.client64 <_api/msl.loadlib.client64>
   msl.loadlib.freeze_server32 <_api/msl.loadlib.freeze_server32>
   msl.loadlib.load_library <_api/msl.loadlib.load_library>
   msl.loadlib.server32 <_api/msl.loadlib.server32>
   msl.loadlib.start_server32 <_api/msl.loadlib.start_server32>
