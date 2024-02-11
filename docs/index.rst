.. _msl-loadlib-welcome:

===========
MSL-LoadLib
===========

This package loads a shared library in Python. It is basically just a thin
wrapper around :mod:`ctypes` (for libraries that use the ``__cdecl`` or
``__stdcall`` calling convention), `Python for .NET`_ (for libraries that
use Microsoft .NET, ``CLR``), Py4J_ (for Java ``.jar`` or ``.class``
files) and comtypes_ (for libraries that use the `Component Object Model`_).

However, the primary advantage is that it is possible to communicate with a
32-bit shared library in 64-bit Python. For various reasons, mainly to do with
the differences in pointer sizes, it is not possible to load a 32-bit shared
library (e.g., .dll, .so, .dylib files) in a 64-bit process, and vice versa.
This package contains a :class:`~msl.loadlib.server32.Server32` class that hosts
a 32-bit library and a :class:`~msl.loadlib.client64.Client64` class that sends
a request to the server to communicate with the 32-bit library as a form of
`inter-process communication`_.

========
Contents
========

.. toctree::
   :maxdepth: 1

   Install <install>
   Load a library <direct>
   Access a 32-bit library in 64-bit Python <interprocess_communication>
   API <api_docs>
   Create a custom 32-bit server <refreeze>
   Source code for the example libraries <examples_source_code>
   FAQ <faq>
   License <license>
   Authors <authors>
   Release Notes <changelog>

.. _Python for .NET: https://pythonnet.github.io/
.. _Py4J: https://www.py4j.org/
.. _comtypes: https://pythonhosted.org/comtypes/#
.. _Component Object Model: https://en.wikipedia.org/wiki/Component_Object_Model
.. _inter-process communication: https://en.wikipedia.org/wiki/Inter-process_communication>
