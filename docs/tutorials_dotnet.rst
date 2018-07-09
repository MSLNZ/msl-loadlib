.. _tutorial_dotnet:

===========================================
Load a 32-bit .NET library in 64-bit Python
===========================================

.. note::
   If you have issues running the example please make sure that you have the
   :ref:`prerequisites <prerequisites>` installed.

This example shows how to access a 32-bit .NET library from a module that is run by a
64-bit Python interpreter by using `inter-process communication
<https://en.wikipedia.org/wiki/Inter-process_communication>`_.
:class:`~msl.examples.loadlib.dotnet32.DotNet32` is the 32-bit server and
:class:`~msl.examples.loadlib.dotnet64.DotNet64` is the 64-bit client.

.. tip::
   The `JetBrains dotPeek <https://www.jetbrains.com/decompiler/>`_ program can be used
   to reliably decompile any .NET assembly into the equivalent C# source code. For example,
   *peeking* inside the :ref:`dotnet_lib32.dll <dotnet-lib>` library, that the
   :class:`~msl.examples.loadlib.dotnet32.DotNet32` class is a wrapper around, gives

   .. image:: _static/dotpeek_lib.png

The following shows that the 32-bit :ref:`dotnet_lib32.dll <dotnet-lib>` library cannot
be loaded in a 64-bit Python interpreter:

.. code-block:: pycon

   >>> from msl.loadlib import LoadLibrary, IS_PYTHON_64BIT
   >>> from msl.examples.loadlib import EXAMPLES_DIR
   >>> IS_PYTHON_64BIT
   True
   >>> net = LoadLibrary(EXAMPLES_DIR + '/dotnet_lib32', 'net')
   Traceback (most recent call last):
     File "<input>", line 1, in <module>
     File "D:\msl\loadlib\load_library.py", line 130, in __init__
       self._assembly = clr.System.Reflection.Assembly.LoadFile(self._path)
   System.BadImageFormatException: Could not load file or assembly 'dotnet_lib32.dll' or one of its dependencies.  is not a valid Win32 application. (Exception from HRESULT: 0x800700C1)
      at System.Reflection.RuntimeAssembly.nLoadFile(String path, Evidence evidence)
      at System.Reflection.Assembly.LoadFile(String path)

However, the 64-bit version of the .NET library can be directly loaded in 64-bit Python:

.. code-block:: pycon

   >>> net = LoadLibrary(EXAMPLES_DIR + '/dotnet_lib64', 'net')
   >>> net
   <LoadLibrary id=0x37c1da0 libtype=DotNet path=D:\msl\examples\loadlib\dotnet_lib64.dll>
   >>> net.lib.StringManipulation.reverse_string('Hello World!')
   '!dlroW olleH'

Instead, create a :class:`~msl.examples.loadlib.dotnet64.DotNet64` client to communicate
with the 32-bit :ref:`dotnet_lib32.dll <dotnet-lib>` library:

.. code-block:: pycon

   >>> from msl.examples.loadlib import DotNet64
   >>> dn = DotNet64()
   >>> dn
   <DotNet64 id=0x1d4ee95 lib=dotnet_lib32.dll address=127.0.0.1:11051>
   >>> dn.lib32_path
   'D:\\msl\\examples\\loadlib\\dotnet_lib32.dll'

Get the names of the classes in the .NET library module, see
:meth:`~msl.examples.loadlib.dotnet64.DotNet64.get_class_names`:

.. code-block:: pycon

   >>> dn.get_class_names()
   ['StringManipulation', 'StaticClass', 'DotNetMSL.BasicMath', 'DotNetMSL.ArrayManipulation']

Add two integers, see :meth:`~msl.examples.loadlib.dotnet64.DotNet64.add_integers`:

.. code-block:: pycon

   >>> dn.add_integers(8, 2)
   10

Divide two C# floating-point numbers, see :meth:`~msl.examples.loadlib.dotnet64.DotNet64.divide_floats`:

.. code-block:: pycon

   >>> dn.divide_floats(4., 5.)
   0.8

Multiple two C# double-precision numbers, see :meth:`~msl.examples.loadlib.dotnet64.DotNet64.multiply_doubles`:

.. code-block:: pycon

   >>> dn.multiply_doubles(872.24, 525.525)
   458383.926

Add or subtract two C# double-precision numbers, see :meth:`~msl.examples.loadlib.dotnet64.DotNet64.add_or_subtract`:

.. code-block:: pycon

   >>> dn.add_or_subtract(99., 9., True)
   108.0
   >>> dn.add_or_subtract(99., 9., False)
   90.0

Multiply a 1D array by a number, see :meth:`~msl.examples.loadlib.dotnet64.DotNet64.scalar_multiply`:

.. code-block:: pycon

   >>> a = [float(val) for val in range(10)]
   >>> a
   [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
   >>> dn.scalar_multiply(2.0, a)
   [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0]

Multiply two matrices, see :meth:`~msl.examples.loadlib.dotnet64.DotNet64.multiply_matrices`:

.. code-block:: pycon

   >>> m1 = [[1., 2., 3.], [4., 5., 6.]]
   >>> m2 = [[1., 2.], [3., 4.], [5., 6.]]
   >>> dn.multiply_matrices(m1, m2)
   [[22.0, 28.0], [49.0, 64.0]]

Reverse a string, see :meth:`~msl.examples.loadlib.dotnet64.DotNet64.reverse_string`:

.. code-block:: pycon

   >>> dn.reverse_string('New Zealand')
   'dnalaeZ weN'

Call the static methods in the ``StaticClass`` class

.. code-block:: pycon

   >>> dn.add_multiple(1, 2, 3, 4, 5)
   15
   >>> dn.concatenate('the ', 'experiment ', 'worked ', False, 'temporarily')
   'the experiment worked '
   >>> dn.concatenate('the ', 'experiment ', 'worked ', True, 'temporarily')
   'the experiment worked temporarily'

Shutdown the server, see :meth:`~msl.loadlib.client64.Client64.shutdown_server32`:

.. code-block:: pycon

   >>> dn.shutdown_server32()

.. note::
   When using a subclass of :class:`~msl.loadlib.client64.Client64` in a script, the
   :meth:`~msl.loadlib.client64.Client64.shutdown_server32` method gets called automatically
   when the instance of the subclass is about to be destroyed and therefore you do not have to call
   the :meth:`~msl.loadlib.client64.Client64.shutdown_server32` method to shutdown the server.
