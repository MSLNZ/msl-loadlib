Welcome to MSL-LoadLib
======================

|docs|

Purpose
-------

Load a shared library into Python.

This package is basically just a thin wrapper around `ctypes
<https://docs.python.org/3/library/ctypes.html>`_ and `Python
for .NET <https://pypi.python.org/pypi/pythonnet/>`_ for loading a shared library
into Python. However, the primary advantage is that it is possible to communicate
with a 32-bit shared library from within 64-bit Python.

Tested in Python 2.7, 3.3 - 3.6. The `examples <http://msl-loadlib.readthedocs.io/en/latest/examples.html>`_
provided are currently only supported in Windows, however **MSL-LoadLib** should work properly with any OS
*(not tested)* that `Python for .NET <https://pypi.python.org/pypi/pythonnet/>`_ supports (and if you don't
care about loading .NET libraries then **MSL-LoadLib** is a pure-python package so it is OS independent).

Example
-------

If you are loading a 64-bit library into 64-bit Python, or a 32-bit library into
32-bit Python, then you can directly load the library using ``msl.loadlib.LoadLibrary``.

Using a 64-bit Python interpreter, load the 64-bit C++ library named `cpp_lib64 <msl/examples/loadlib/cpp_lib.cpp>`_.
By default, ``msl.loadlib.LoadLibrary`` loads a library using
`ctypes.CDLL <https://docs.python.org/3/library/ctypes.html#ctypes.CDLL>`_.

.. code:: python

   >>> import msl.loadlib
   >>> msl.loadlib.IS_PYTHON_64BIT
   True
   >>> cpp = msl.loadlib.LoadLibrary('./cpp_lib64')
   >>> cpp
   LoadLibrary object at 0x3e9f750; libtype=ctypes.CDLL; path=D:/examples/cpp_lib64.dll
   >>> cpp.lib
   <CDLL 'D:/examples/cpp_lib64.dll', handle af1e0000 at 0x3e92f90>

Call the ``cpp_lib64.add`` function that calculates the sum of two integers

.. code:: python

   >>> import ctypes
   >>> cpp.lib.add(ctypes.c_int32(1), ctypes.c_int32(2))
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

Install **MSL-LoadLib** using pip::

   $ pip install git+https://github.com/mslnz/msl-loadlib

*Note: To run the above command, pip requires that* git_ *is installed and for the* **git** *command to be available on your path.*

Developers Guide
----------------

**MSL-LoadLib** uses pytest_ and coverage_ for testing the source code and sphinx_ for creating the documentation.

Build the documentation::

   $ python setup.py docs

Run the tests::

   $ python setup.py tests

Automatically create the API documentation from the docstrings in the source code (uses sphinx-apidoc_).

*NOTE: The* ``docs/_autosummary`` *folder that is created by running this command is
automatically generated and therefore not kept. If you want to keep the files located in*
``docs/_autosummary`` *you should rename the folder to, for example,* ``docs/_api`` *and then
the changes made to the files in the* ``docs/_api`` *folder will be kept.*::

   $ python setup.py apidoc
   
Create a wheel for distributing **MSL-LoadLib**::

   $ python setup.py wheel

Install from source::

   $ python setup.py install

.. |docs| image:: https://readthedocs.org/projects/msl-loadlib/badge/?version=latest
   :target: http://msl-loadlib.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
   :scale: 100%

.. _git: https://git-scm.com/download
.. _pytest: http://doc.pytest.org/en/latest/
.. _sphinx: http://www.sphinx-doc.org/en/stable/
.. _sphinx-apidoc: http://www.sphinx-doc.org/en/stable/man/sphinx-apidoc.html
.. _coverage: http://coverage.readthedocs.io/en/latest/index.html

