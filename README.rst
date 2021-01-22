===========
MSL-LoadLib
===========

|docs| |pypi| |travis| |appveyor|

This package is used to load a shared library in Python. It is basically just a thin wrapper
around ctypes_ (for libraries that use the ``__cdecl`` or ``__stdcall`` calling convention),
`Python for .NET`_ (for libraries that use Microsoft's .NET Framework, ``CLR``), Py4J_
(for Java ``.jar`` or ``.class`` files) and comtypes_ (for libraries that use the
`Component Object Model`_).

However, the primary advantage is that it is possible to communicate with a 32-bit shared
library from 64-bit Python.

Tested in Python 2.7, 3.5+. The `examples <https://msl-loadlib.readthedocs.io/en/latest/direct.html>`_
provided are currently only supported in Windows and Linux.

**MSL-LoadLib** is a pure-python package, but, `Python for .NET`_ depends on the .NET Common Language
Runtime (CLR) on Windows and Mono Runtime on Linux and macOS and Py4J_ depends on having a
`Java Virtual Machine`_ installed.

Install
-------

To install **MSL-LoadLib** run:

.. code-block:: console

   pip install msl-loadlib

Alternatively, using the `MSL Package Manager`_ run:

.. code-block:: console

   msl install loadlib

Optional dependencies:

* `Python for .NET`_
* Py4J_
* comtypes_

To set up your environment on Linux, please follow the instructions on the
`prerequisites <https://msl-loadlib.readthedocs.io/en/latest/install.html#prerequisites>`_
section of the documentation.

Examples
--------

If you are loading a 64-bit library in 64-bit Python, or a 32-bit library in 32-bit Python,
then you can directly load the library using ``LoadLibrary``.

The following examples load a 64-bit library in a 64-bit Python interpreter. If you are using a 32-bit
Python interpreter then replace the **64** with **32** in the filename.

Import the ``LoadLibrary`` class and the directory where the example libraries are located

.. code-block:: pycon

   >>> from msl.loadlib import LoadLibrary
   >>> from msl.examples.loadlib import EXAMPLES_DIR

If the file extension is not included then a default extension, ``.dll`` (Windows) or ``.so`` (Linux), is used.

Load a `C++ <https://github.com/MSLNZ/msl-loadlib/blob/master/msl/examples/loadlib/cpp_lib.cpp>`_ library
and call the ``add`` function

.. code-block:: pycon

   >>> cpp = LoadLibrary(EXAMPLES_DIR + '/cpp_lib64')
   >>> cpp.lib.add(1, 2)
   3

Load a `FORTRAN <https://github.com/MSLNZ/msl-loadlib/blob/master/msl/examples/loadlib/fortran_lib.f90>`_
library and call the ``factorial`` function

.. code-block:: pycon

   >>> fortran = LoadLibrary(EXAMPLES_DIR + '/fortran_lib64')

With a FORTRAN library you must pass values by reference using ctypes_, and, since the returned value is not
of type ``int`` we must configure ctypes_ for a value of type ``double`` to be returned

.. code-block:: pycon

   >>> from ctypes import byref, c_int, c_double
   >>> fortran.lib.factorial.restype = c_double
   >>> fortran.lib.factorial(byref(c_int(37)))
   1.3763753091226343e+43

Load a `.NET <https://github.com/MSLNZ/msl-loadlib/blob/master/msl/examples/loadlib/dotnet_lib.cs>`_ library
and call the ``reverse_string`` function, we must specify that the library type is a .NET library by passing
in the ``'net'`` argument

.. code-block:: pycon

   >>> net = LoadLibrary(EXAMPLES_DIR + '/dotnet_lib64.dll', 'net')
   >>> net.lib.StringManipulation().reverse_string('abcdefghijklmnopqrstuvwxyz')
   'zyxwvutsrqponmlkjihgfedcba'

Load `Java <https://github.com/MSLNZ/msl-loadlib/blob/master/msl/examples/loadlib/Trig.java>`_ byte code
and call the ``cos`` function

.. code-block:: pycon

   >>> java = LoadLibrary(EXAMPLES_DIR + '/Trig.class')
   >>> java.lib.Trig.cos(1.234)
   0.33046510807172985

Python interacts with the `Java Virtual Machine`_ via a local network socket and therefore the connection
needs to be closed when you are done using the Java library

.. code-block:: pycon

   >>> java.gateway.shutdown()

To load a `Component Object Model`_ (COM) library pass in the library's Program ID.
*NOTE: This example will only work on Windows.*

Here we load the FileSystemObject_ library and include the ``'com'`` argument to indicate that
it is a COM library.

.. invisible-code-block: pycon

   >>> SKIP_IF_NOT_WINDOWS()

.. code-block:: pycon

   >>> com = LoadLibrary('Scripting.FileSystemObject', 'com')

If creating the `com` object in the previous command raises

.. code-block:: console

   OSError: [WinError -2147417850] Cannot change thread mode after it is set

then perform the following and try again

.. code-block:: pycon

   >>> import sys
   >>> sys.coinit_flags = 0

We then use the library to create, edit and close a text file

.. code-block:: pycon

   >>> fp = com.lib.CreateTextFile('a_new_file.txt')
   >>> fp.WriteLine('This is a test')
   0
   >>> fp.Close()
   0

.. invisible-code-block: pycon

   >>> import os
   >>> os.remove('a_new_file.txt')

`Inter-process communication <ipc_>`_ is used to access a 32-bit shared library from a module that is
running within a 64-bit Python interpreter. The procedure uses a client-server protocol where the client
is a subclass of ``msl.loadlib.Client64`` and the server is a subclass of ``msl.loadlib.Server32``.
See the `tutorials <https://msl-loadlib.readthedocs.io/en/latest/interprocess_communication.html>`_ for
examples on how to implement `inter-process communication <ipc_>`_.

Documentation
-------------

The documentation for **MSL-LoadLib** can be found `here <https://msl-loadlib.readthedocs.io/en/latest/index.html>`_.

.. |docs| image:: https://readthedocs.org/projects/msl-loadlib/badge/?version=stable
   :target: https://msl-loadlib.readthedocs.io/en/stable/
   :alt: Documentation Status

.. |pypi| image:: https://badge.fury.io/py/msl-loadlib.svg
   :target: https://badge.fury.io/py/msl-loadlib

.. |travis| image:: https://img.shields.io/travis/MSLNZ/msl-loadlib/master.svg?label=Travis-CI
   :target: https://travis-ci.org/MSLNZ/msl-loadlib

.. |appveyor| image:: https://img.shields.io/appveyor/ci/jborbely/msl-loadlib/master.svg?label=AppVeyor
   :target: https://ci.appveyor.com/project/jborbely/msl-loadlib/branch/master

.. _ctypes: https://docs.python.org/3/library/ctypes.html
.. _Python for .NET: https://pythonnet.github.io/
.. _Py4J: https://www.py4j.org/
.. _ipc: https://en.wikipedia.org/wiki/Inter-process_communication
.. _Java Virtual Machine: https://en.wikipedia.org/wiki/Java_virtual_machine
.. _MSL Package Manager: https://msl-package-manager.readthedocs.io/en/latest/
.. _comtypes: https://pythonhosted.org/comtypes/#
.. _Component Object Model: https://en.wikipedia.org/wiki/Component_Object_Model
.. _FileSystemObject: https://docs.microsoft.com/en-us/office/vba/language/reference/user-interface-help/filesystemobject-object
