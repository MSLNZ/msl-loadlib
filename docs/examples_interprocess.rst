Use inter-process communication to access a 32-bit shared library from 64-bit Python
====================================================================================

This section of the documentation shows examples for how a module running within a
64-bit Python interpreter can communicate with a 32-bit shared library by using
`inter-process communication <https://en.wikipedia.org/wiki/Inter-process_communication>`_.

The following table summarizes the example modules that are available.

Modules that end in **32** contain a class that is a subclass of
:class:`~msl.loadlib.server32.Server32`. This subclass is a wrapper around
a 32-bit library and is hosted on a 32-bit server.

Modules that end in **64** contain a class that is a subclass of
:class:`~msl.loadlib.client64.Client64`. This subclass sends a request to
the corresponding :class:`~msl.loadlib.server32.Server32` subclass to
communicate with the 32-bit library.

See the :ref:`tutorials <tutorials>` for an overview on how to use these example modules.

.. autosummary::

   msl.examples.loadlib.dummy32 <msl.examples.loadlib.dummy32>
   msl.examples.loadlib.dummy64 <msl.examples.loadlib.dummy64>
   msl.examples.loadlib.cpp32 <msl.examples.loadlib.cpp32>
   msl.examples.loadlib.cpp64 <msl.examples.loadlib.cpp64>
   msl.examples.loadlib.kernel32 <msl.examples.loadlib.kernel32>
   msl.examples.loadlib.kernel64 <msl.examples.loadlib.kernel64>
   msl.examples.loadlib.dotnet32 <msl.examples.loadlib.dotnet32>
   msl.examples.loadlib.dotnet64 <msl.examples.loadlib.dotnet64>
   msl.examples.loadlib.fortran32 <msl.examples.loadlib.fortran32>
   msl.examples.loadlib.fortran64 <msl.examples.loadlib.fortran64>

.. toctree::

   cpp_source
   fortran_source
