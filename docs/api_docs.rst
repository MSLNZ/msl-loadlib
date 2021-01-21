.. _api:

=============================
MSL-LoadLib API Documentation
=============================

The root package is

.. autosummary::

   msl.loadlib

which has the following class for directly loading a shared library,

.. autosummary::

   ~msl.loadlib.load_library.LoadLibrary

the following client-server classes for communicating with a 32-bit library
from 64-bit Python,

.. autosummary::

   ~msl.loadlib.client64.Client64
   ~msl.loadlib.server32.Server32

a function to create a frozen_ 32-bit server

.. autosummary::

   ~msl.loadlib.freeze_server32

and some general helper functions

.. autosummary::

   ~msl.loadlib.utils

Package Structure
-----------------

.. toctree::

   msl.loadlib <_api/msl.loadlib>
   msl.loadlib.client64 <_api/msl.loadlib.client64>
   msl.loadlib.exceptions <_api/msl.loadlib.exceptions>
   msl.loadlib.freeze_server32 <_api/msl.loadlib.freeze_server32>
   msl.loadlib.load_library <_api/msl.loadlib.load_library>
   msl.loadlib.server32 <_api/msl.loadlib.server32>
   msl.loadlib.start_server32 <_api/msl.loadlib.start_server32>
   msl.loadlib.utils <_api/msl.loadlib.utils>

Example modules for communicating with a 32-bit library from 64-bit Python
--------------------------------------------------------------------------

.. toctree::

   _api/msl.examples.loadlib

.. _frozen: https://www.pyinstaller.org/
