===========
MSL-LoadLib
===========

This package is used to load a shared library in to Python. It is basically just a
thin wrapper around `ctypes <https://docs.python.org/3/library/ctypes.html>`_ (for libraries
using the ``__cdecl`` and ``__stdcall`` calling convention),
`Python for .NET <http://pythonnet.github.io/>`_ (for libraries using Microsoft's
.NET Framework) and `Py4J <https://www.py4j.org/>`_ (for Java ARchive libraries, ``JAR``).

However, the primary advantage is that it is possible to communicate with a 32-bit
shared library in 64-bit Python. For various reasons, mainly to do with the
differences in pointer sizes, it is not possible to load a 32-bit shared library
(e.g., .dll, .so, .dylib files) in to a 64-bit process, and vice versa. This package
contains a :class:`~msl.loadlib.server32.Server32` class that hosts a 32-bit library and
a :class:`~msl.loadlib.client64.Client64` class that sends a request to the server to
communicate with the 32-bit library as a form of `inter-process communication
<https://en.wikipedia.org/wiki/Inter-process_communication>`_.

.. toctree::
   :maxdepth: 2

   Install <install>
   Load a library <usage>
   API Documentation <api_docs>
   Examples <examples>
   Tutorials <tutorials>
   License <license>
   Authors <authors>
   Changelog <changelog>

=====
Index
=====

* :ref:`modindex`
