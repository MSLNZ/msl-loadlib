.. _inter-process-communication:

Access a 32-bit library in 64-bit Python
========================================

This section of the documentation shows examples for how a module running within a
64-bit Python interpreter can communicate with a 32-bit shared library by using
`inter-process communication <https://en.wikipedia.org/wiki/Inter-process_communication>`_.
The method that is used to allow a 32-bit and a 64-bit process to exchange information is
by use of a file. The :mod:`pickle` module is used to (de)serialize Python objects.

The following table summarizes the example modules that are available.

Modules that end in **32** contain a class that is a subclass of
:class:`~msl.loadlib.server32.Server32`. This subclass is a wrapper around
a 32-bit library and is hosted on a 32-bit server.

Modules that end in **64** contain a class that is a subclass of
:class:`~msl.loadlib.client64.Client64`. This subclass sends a request to
the corresponding :class:`~msl.loadlib.server32.Server32` subclass to
communicate with the 32-bit library.

.. autosummary::

   ~msl.examples.loadlib.echo32
   ~msl.examples.loadlib.echo64
   ~msl.examples.loadlib.cpp32
   ~msl.examples.loadlib.cpp64
   ~msl.examples.loadlib.fortran32
   ~msl.examples.loadlib.fortran64
   ~msl.examples.loadlib.dotnet32
   ~msl.examples.loadlib.dotnet64
   ~msl.examples.loadlib.kernel32
   ~msl.examples.loadlib.kernel64
   ~msl.examples.loadlib.labview32
   ~msl.examples.loadlib.labview64

The following illustrates a minimal usage example. The **cpp_lib32.dll** file is a
32-bit C++ library that cannot be loaded from a module that is running within a 64-bit Python
interpreter. This library gets loaded by the **MyServer** class (that is a subclass of
:class:`~msl.loadlib.server32.Server32`) which is running within a 32-bit executable,
see :mod:`~msl.loadlib.start_server32`. **MyServer** hosts the library at the specified host
address and port number. Any class that is a subclass of :class:`~msl.loadlib.server32.Server32`
*must* provide three arguments in its constructor: ``host``, ``port`` and ``quiet``
(in that order) and ``**kwargs``. Otherwise the 32-bit executable cannot create an instance of the
subclass.

.. code-block:: python

    # my_server.py

    from msl.loadlib import Server32

    class MyServer(Server32):
        """A wrapper around a 32-bit C++ library, 'cpp_lib32.dll', that has an 'add' function."""

        def __init__(self, host, port, quiet, **kwargs):
            # Load the 'cpp_lib32' shared-library file using ctypes.CDLL.
            # The optional kwargs are only used by MyServer and are not passed to Server32.
            super(MyServer, self).__init__('cpp_lib32.dll', 'cdll', host, port, quiet)

        def add(self, a, b):
            # The Server32 class has a 'lib' property that is a reference to the ctypes.CDLL object.
            # The shared library’s 'add' function takes two integers as inputs and returns the sum.
            return self.lib.add(a, b)

Keyword arguments, ``**kwargs``, can be passed to the server either from the client (see,
:class:`~msl.loadlib.client64.Client64`) or by manually starting the server from the command line
(see, :class:`~msl.loadlib.start_server32`). However, the data types for the values of the ``**kwargs`` are not
preserved (since they are ultimately parsed from the command line). Therefore, all data types for
the *kwargs* values will be of type :class:`str` at the constructor of the :class:`~msl.loadlib.server32.Server32`
subclass. You must convert each value to the appropriate data type. This ``**kwargs`` variable
is the only variable that the data type is not preserved for the client-server protocol (see, the
`"Echo" example <tutorials_echo.html>`_ that shows that data types are preserved between client-server
method calls).

**MyClient** is a subclass of :class:`~msl.loadlib.client64.Client64` which sends a request to
**MyServer** to call the ``add`` function in the shared library. **MyServer** processes the
request and sends the response back to **MyClient**.

.. code-block:: python

    # my_client.py

    from msl.loadlib import Client64

    class MyClient(Client64):
        """Send a request to 'MyServer' to execute the 'add' method and get the response."""

        def __init__(self):
            # Specify the name of the Python module to execute on the 32-bit server (i.e., 'my_server')
            super(MyClient, self).__init__(module32='my_server')

        def add(self, a, b):
            # The Client64 class has a 'request32' method to send a request to the 32-bit server.
            # Send the 'a' and 'b' arguments to the 'add' method in MyServer.
            return self.request32('add', a, b)

The **MyClient** class would then be used as follows

.. code-block:: pycon

   >>> from my_client import MyClient
   >>> c = MyClient()
   >>> c.add(1, 2)
   3

The following examples are provided for communicating with different libraries that were
compiled in different programming languages or using different calling conventions:

.. toctree::

   "Echo" <tutorials_echo>
   C++ <tutorials_cpp>
   FORTRAN <tutorials_fortran>
   Microsoft .NET Framework <tutorials_dotnet>
   Windows __stdcall <tutorials_stdcall>
   LabVIEW <tutorials_labview>
