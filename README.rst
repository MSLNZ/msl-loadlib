Welcome to MSL-LoadLib
======================

|docs|

Purpose
-------

Load a shared library into Python.

This package is basically just a thin wrapper around `ctypes <https://docs.python.org/3/library/ctypes.html>`_ and
`Python for .NET <https://pypi.python.org/pypi/pythonnet/>`_ for loading a shared library into Python. However,
the primary advantage is that it is possible to communicate with a 32-bit shared library from 64-bit Python.

Tested in Python 2.7, 3.3 - 3.6. The `examples <http://msl-loadlib.readthedocs.io/en/latest/examples.html>`_
provided are currently only supported in Windows and Linux, however **MSL-LoadLib** should work properly with any OS
*(not tested)* that `Python for .NET <https://pypi.python.org/pypi/pythonnet/>`_ supports (and if you don't
care about loading .NET libraries then **MSL-LoadLib** is a pure-python package so it is OS independent).

Example
-------

If you are loading a 64-bit library into 64-bit Python, or a 32-bit library into 32-bit Python, then you can
directly load the library using ``msl.loadlib.LoadLibrary``.

Using a 64-bit Python interpreter, load the 64-bit C++ library named `cpp_lib64 <msl/examples/loadlib/cpp_lib.cpp>`_.
By default, ``msl.loadlib.LoadLibrary`` loads a library using
`ctypes.CDLL <https://docs.python.org/3/library/ctypes.html#ctypes.CDLL>`_.

.. code:: python

   >>> from msl.loadlib import LoadLibrary
   >>> cpp = LoadLibrary('./cpp_lib64')
   >>> cpp
   LoadLibrary object at 0x3e9f750; libtype=CDLL; path=D:\cpp_lib64.dll
   >>> cpp.lib
   <CDLL 'D:\cpp_lib64.dll', handle af1e0000 at 0x3e92f90>

Call the ``cpp_lib64.add`` function that calculates the sum of two integers

.. code:: python

   >>> cpp.lib.add(1, 2)
   3

`Inter-process communication <https://en.wikipedia.org/wiki/Inter-process_communication>`_ is used
to access a 32-bit shared library from a module that is running within a 64-bit Python interpreter.
The procedure uses a client-server protocol where the client is a subclass of ``msl.loadlib.Client64``
and the server is a subclass of ``msl.loadlib.Server32``. See the `tutorials 
<http://msl-loadlib.readthedocs.io/en/latest/tutorials.html>`_ for examples on how to implement
`inter-process communication <https://en.wikipedia.org/wiki/Inter-process_communication>`_.

Documentation
-------------

The documentation for **MSL-LoadLib** can be found `here <http://msl-loadlib.readthedocs.io/en/latest/index.html>`_.

Install
-------

If using Windows you can install **MSL-LoadLib** using pip::

   pip install https://github.com/MSLNZ/msl-loadlib/archive/master.zip

For installation on Linux, please follow the instructions on the
`prerequisites <http://msl-loadlib.readthedocs.io/en/latest/install.html#prerequisites>`_ section of the documentation.

Developers Guide
----------------

**MSL-LoadLib** uses pytest_ for testing the source code and sphinx_ for creating the documentation.

Run the tests (a coverage_ report is generated in the **htmlcov/index.html** file)::

   python setup.py test

Build the documentation, which can be viewed by opening the **docs/_build/html/index.html** file::

   python setup.py docs

Automatically create the API documentation from the docstrings in the source code (uses sphinx-apidoc_)::

   python setup.py apidoc

*NOTE: By default, the* **docs/_autosummary** *folder that is created by running the* **apidoc** *command is
automatically generated (it will overwrite existing files). As such, it is excluded from the repository (i.e., this
folder is specified in the* **.gitignore** *file). If you want to keep the files located in* **docs/_autosummary** *you
can rename the folder to be, for example,* **docs/_api** *and then the changes made to the files in the* **docs/_api**
*folder will be kept and will be included in the repository.*

.. |docs| image:: https://readthedocs.org/projects/msl-loadlib/badge/?version=latest
   :target: http://msl-loadlib.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
   :scale: 100%

.. _git: https://git-scm.com/download
.. _pytest: http://doc.pytest.org/en/latest/
.. _sphinx: http://www.sphinx-doc.org/en/stable/
.. _sphinx-apidoc: http://www.sphinx-doc.org/en/stable/man/sphinx-apidoc.html
.. _coverage: http://coverage.readthedocs.io/en/latest/index.html
