.. _msl-loadlib-welcome:

===========
MSL-LoadLib
===========

This package is used to load a shared library in Python. It is basically just a
thin wrapper around :mod:`ctypes` (for libraries that use the ``__cdecl`` or ``__stdcall``
calling convention), `Python for .NET <https://pythonnet.github.io/>`_ (for libraries that use
Microsoft's .NET Framework, ``CLR``), `Py4J <https://www.py4j.org/>`_ (for Java ``.jar`` or
``.class`` files) and `comtypes <https://pythonhosted.org/comtypes/#>`_ (for libraries that use
the `Component Object Model <https://en.wikipedia.org/wiki/Component_Object_Model>`_).

However, the primary advantage is that it is possible to communicate with a 32-bit
shared library in 64-bit Python. For various reasons, mainly to do with the
differences in pointer sizes, it is not possible to load a 32-bit shared library
(e.g., .dll, .so, .dylib files) in to a 64-bit process, and vice versa. This package
contains a :class:`~msl.loadlib.server32.Server32` class that hosts a 32-bit library and
a :class:`~msl.loadlib.client64.Client64` class that sends a request to the server to
communicate with the 32-bit library as a form of `inter-process communication
<https://en.wikipedia.org/wiki/Inter-process_communication>`_.

========
Contents
========

.. toctree::
   :maxdepth: 2

   Install <install>
   Load a library <direct>
   Access a 32-bit library in 64-bit Python <interprocess_communication>
   API documentation <api_docs>
   Source code for the example libraries <examples_source_code>
   Re-freezing the 32-bit server <refreeze>
   License <license>
   Authors <authors>
   Changelog <changelog>

=====
Index
=====

* :ref:`modindex`
