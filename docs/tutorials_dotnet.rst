.. _tutorial_dotnet:

===========================================
Load a 32-bit .NET library in 64-bit Python
===========================================

This example shows how to access a 32-bit .NET library from 64-bit Python.
:class:`~msl.examples.loadlib.dotnet32.DotNet32` is the 32-bit server and
:class:`~msl.examples.loadlib.dotnet64.DotNet64` is the 64-bit client.
The source code of the C# program is available :ref:`here <dotnet-lib>`.

.. note::
   If you have issues running the example please make sure that you have the
   :ref:`prerequisites <loadlib-prerequisites>` installed for your operating system.

.. tip::
   The `JetBrains dotPeek`_ program can be used to decompile a .NET assembly into
   the equivalent source code. For example, *peeking* inside the
   :ref:`dotnet_lib32.dll <dotnet-lib>` library, that the
   :class:`~msl.examples.loadlib.dotnet32.DotNet32` class is a wrapper around, gives

   .. image:: _static/dotpeek_lib.png

Create a :class:`~msl.examples.loadlib.dotnet64.DotNet64` client to communicate
with the 32-bit :ref:`dotnet_lib32.dll <dotnet-lib>` library

.. invisible-code-block: pycon

   >>> SKIP_IF_WINDOWS_GITHUB_ACTIONS()

.. code-block:: pycon

   >>> from msl.examples.loadlib import DotNet64
   >>> dn = DotNet64()

Get the names of the classes in the .NET library module, see
:meth:`~msl.examples.loadlib.dotnet64.DotNet64.get_class_names`

.. code-block:: pycon

   >>> dn.get_class_names()
   ['StringManipulation', 'StaticClass', 'DotNetMSL.BasicMath', 'DotNetMSL.ArrayManipulation']

Add two integers, see :meth:`~msl.examples.loadlib.dotnet64.DotNet64.add_integers`

.. code-block:: pycon

   >>> dn.add_integers(8, 2)
   10

Divide two C# floating-point numbers, see
:meth:`~msl.examples.loadlib.dotnet64.DotNet64.divide_floats`

.. code-block:: pycon

   >>> dn.divide_floats(3., 2.)
   1.5

Multiple two C# double-precision numbers, see
:meth:`~msl.examples.loadlib.dotnet64.DotNet64.multiply_doubles`

.. code-block:: pycon

   >>> dn.multiply_doubles(872.24, 525.525)
   458383.926

Add or subtract two C# double-precision numbers, see
:meth:`~msl.examples.loadlib.dotnet64.DotNet64.add_or_subtract`

.. code-block:: pycon

   >>> dn.add_or_subtract(99., 9., True)
   108.0
   >>> dn.add_or_subtract(99., 9., False)
   90.0

Multiply a 1D array by a number, see
:meth:`~msl.examples.loadlib.dotnet64.DotNet64.scalar_multiply`

.. code-block:: pycon

   >>> a = [float(val) for val in range(10)]
   >>> a
   [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
   >>> dn.scalar_multiply(2.0, a)
   [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0]

Multiply two matrices, see
:meth:`~msl.examples.loadlib.dotnet64.DotNet64.multiply_matrices`

.. code-block:: pycon

   >>> m1 = [[1., 2., 3.], [4., 5., 6.]]
   >>> m2 = [[1., 2.], [3., 4.], [5., 6.]]
   >>> dn.multiply_matrices(m1, m2)
   [[22.0, 28.0], [49.0, 64.0]]

Reverse a string, see
:meth:`~msl.examples.loadlib.dotnet64.DotNet64.reverse_string`

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

Shutdown the 32-bit server when you are done communicating with the 32-bit library

.. code-block:: pycon

   >>> stdout, stderr = dn.shutdown_server32()

.. _JetBrains dotPeek: https://www.jetbrains.com/decompiler/