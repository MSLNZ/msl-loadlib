.. _examples:

====================
MSL-LoadLib Examples
====================

.. toctree::

   examples_direct
   examples_interprocess
   Server32-Client64 modules <_api/msl.examples.loadlib>

.. note::
   The examples are currently only supported in Windows simply because the :ref:`C++ <cpp-lib>` and
   :ref:`FORTRAN <fortran-lib>` libraries have only been compiled into Windows DLL files. The
   :ref:`kernel32 <tutorial_stdcall>` example is only valid on Windows (since it uses **stdcall**)
   and the :ref:`.NET <tutorial_dotnet>` example uses a library for which the source code is not available.
   The source code for the :ref:`C++ <cpp-lib>` and :ref:`FORTRAN <fortran-lib>` libraries are provided.
