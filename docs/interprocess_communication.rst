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
*must* provide two arguments in its constructor: ``host`` and ``port`` (in that order) and
``**kwargs``. Otherwise the 32-bit executable cannot create an instance of the subclass.

.. code-block:: python

    # my_server.py

    from msl.loadlib import Server32

    class MyServer(Server32):
        """A wrapper around a 32-bit C++ library, 'cpp_lib32.dll', that has an 'add' function."""

        def __init__(self, host, port, **kwargs):
            # Load the 'cpp_lib32' shared-library file using ctypes.CDLL.
            super(MyServer, self).__init__('cpp_lib32.dll', 'cdll', host, port)

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
   :maxdepth: 1

   "Echo" <tutorials_echo>
   C++ <tutorials_cpp>
   FORTRAN <tutorials_fortran>
   Microsoft .NET Framework <tutorials_dotnet>
   Windows __stdcall <tutorials_stdcall>
   LabVIEW <tutorials_labview>

.. tip::

    If you find yourself repeatedly implementing each method in your :class:`~msl.loadlib.client64.Client64`
    subclass in the following way (i.e., you are essentially duplicating the code for each method)

    .. code-block:: python

        from msl.loadlib import Client64

        class LinearAlgebra(Client64):

            def __init__(self):
                super(LinearAlgebra, self).__init__(module32='linear_algebra_32.py')

            def solve(self, matrix, vector):
                return self.request32('solve', matrix, vector)

            def eigenvalues(self, matrix):
                return self.request32('eigenvalues', matrix)

            def stdev(self, data, as_population=True)
                return self.request32('stdev', data, as_population=as_population)

            def determinant(self, matrix):
                return self.request32('determinant', matrix)

            def cross_product(self, vector1, vector2):
                return self.request32('cross_product', vector1, vector2)

    Then you can simplify the implementation by defining your :class:`~msl.loadlib.client64.Client64`
    subclass as

    .. code-block:: python

        from msl.loadlib import Client64

        class LinearAlgebra(Client64):

            def __init__(self):
                super(LinearAlgebra, self).__init__(module32='linear_algebra_32.py')

            def __getattr__(self, method32):
                def send(*args, **kwargs):
                    return self.request32(method32, *args, **kwargs)
                return send

    and you will get the same behaviour. If you call a method that does not exist on the
    :class:`~msl.loadlib.server32.Server32` subclass or if you specify the wrong number of
    arguments or keyword arguments then a :class:`~msl.loadlib.exceptions.Server32Error`
    will be raised.

    There are situations where you may want to explicitly write some (or all) of the methods in the
    :class:`~msl.loadlib.client64.Client64` subclass in addition to (or instead of) implementing the
    :obj:`~object.__getattr__` method, e.g.,

    * you are writing an API for others to use and you want features like autocomplete or
      docstrings to be available in the IDE that the person using your API is using
    * you want the :class:`~msl.loadlib.client64.Client64` subclass to do error checking on the
      ``*args``, ``**kwargs`` and/or on the result from the :class:`~msl.loadlib.server32.Server32`
      subclass (this allows you to have control over the type of :ref:`Exception <bltin-exceptions>`
      that is raised because if the :class:`~msl.loadlib.server32.Server32` subclass raises an
      exception then it is a :class:`~msl.loadlib.exceptions.Server32Error`)
    * you want to modify the returned object from a particular :class:`~msl.loadlib.server32.Server32`
      method, for example, a :class:`list` is returned but you want the corresponding
      :class:`~msl.loadlib.client64.Client64` method to return a :class:`numpy.ndarray`
