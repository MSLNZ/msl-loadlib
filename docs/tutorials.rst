.. _tutorials:

============================================================
Tutorials: Access a 32-bit shared library from 64-bit Python
============================================================

These tutorials show you how you can use the :ref:`msl.loadlib <api>` package to access a 32-bit
shared library from a module that is running within a 64-bit Python interpreter. The procedure
implements a client-server protocol, as a type of `inter-process communication
<https://en.wikipedia.org/wiki/Inter-process_communication>`_, where the client is a subclass of
:class:`~msl.loadlib.client64.Client64` and the server is a subclass of
:class:`~msl.loadlib.server32.Server32`.

The following illustrates a minimal usage example. The **cpp_lib32.dll** file is a
32-bit C++ library that cannot be loaded from a module that is running within a 64-bit Python
interpreter. This library gets loaded by the **MyServer** class (that is a subclass of
:class:`~msl.loadlib.server32.Server32`) which is running within a 32-bit executable,
see :mod:`~msl.loadlib.start_server32`. **MyServer** hosts the library at the specified host
address and port number. Any class that is a subclass of :class:`~msl.loadlib.server32.Server32`
**must** provide three arguments in its constructor: ``host``, ``port`` and ``quiet``
(in that order) and ``**kwargs``. Otherwise the 32-bit executable cannot create an instance of the
subclass.

.. code-block:: python

    ## my_server.py

    from msl.loadlib import Server32

    class MyServer(Server32):
        """A wrapper around a 32-bit C++ library, 'cpp_lib32', that has an 'add' function."""

        def __init__(self, host, port, quiet, **kwargs):
            # Load the 'cpp_lib32' shared-library file using ctypes.CDLL
            Server32.__init__(self, 'cpp_lib32', 'cdll', host, port, quiet)

        def add(self, a, b):
            # The Server32 class has a 'lib' attribute that is a reference to the ctypes.CDLL object.
            # The shared library’s 'add' function takes two integers as inputs and returns the sum.
            return self.lib.add(ctypes.c_int32(a), ctypes.c_int32(b))

Keyword arguments, ``**kwargs``, can be passed to the server either from the client (see,
:class:`~msl.loadlib.client64.Client64`) or by manually starting the server from the command line
(see, :class:`~msl.loadlib.start_server32`). However, the data types for the values are not
preserved (since they are ultimately parsed from the command line). Therefore, all data types for
each value will be of type :obj:`str` at the constructor of the :class:`~msl.loadlib.server32.Server32`
subclass. You must convert each value to the appropriate data type. This ``**kwargs`` variable
is the only variable that the data type is not preserved for the client-server protocol (see, the
`"Dummy" example <tutorials_dummy.html>`_ that shows that data types are preserved between client-server
function calls).

**MyClient** is a subclass of :class:`~msl.loadlib.client64.Client64` which sends a request to
**MyServer** to call the ``add`` function in the shared library. **MyServer** processes the
request and sends the response back to **MyClient**.

.. code-block:: python

    from msl.loadlib import Client64

    class MyClient(Client64):
        """Send a request to 'MyServer' to execute the 'add' method and get the response."""

        def __init__(self):
            # Use the default 'localhost' address to start the 'my_server.py' module
            Client64.__init__(self, module32='my_server')

        def add(self, a, b):
            # The Client64 class has a 'request32' method to send a request to the 32-bit server.
            # Send the 'a' and 'b' arguments to the 'add' method in MyServer.
            return self.request32('add', a, b)

The following tutorials are provided for communicating with different libraries that were
compiled in different programming languages or using different calling conventions:

.. toctree::

   "Dummy" example <tutorials_dummy>
   C++ library <tutorials_cpp>
   Windows stdcall library <tutorials_stdcall>
   FORTRAN library <tutorials_fortran>
   .NET Framework library <tutorials_dotnet>
