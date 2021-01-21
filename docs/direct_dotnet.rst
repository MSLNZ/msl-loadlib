.. _direct_dotnet:

Microsoft .NET Framework
------------------------
Load a 64-bit C# library (a .NET Framework) in 64-bit Python (view the
:ref:`C# source code <dotnet-lib>`). Include the ``'net'`` argument to
indicate that the ``.dll`` file is for the .NET Framework.
*To load the 32-bit version in 32-bit Python use* ``'/dotnet_lib32.dll'``.

.. tip::

   ``'clr'`` is an alias for ``'net'`` and can also be used as the `libtype`

.. invisible-code-block: pycon

   >>> SKIP_IF_32BIT()

.. code-block:: pycon

   >>> from msl.loadlib import LoadLibrary
   >>> from msl.examples.loadlib import EXAMPLES_DIR
   >>> net = LoadLibrary(EXAMPLES_DIR + '/dotnet_lib64.dll', 'net')
   >>> net
   <LoadLibrary libtype=DotNet path=...dotnet_lib64.dll>
   >>> net.assembly
   <System.Reflection.RuntimeAssembly object at ...>
   >>> net.lib
   <DotNet path=...dotnet_lib64.dll>

The :ref:`dotnet_lib64 <dotnet-lib>` library contains a reference to the
``DotNetMSL`` module (which is a C# namespace), the ``StaticClass`` class,
the ``StringManipulation`` class and the System_ namespace

.. code-block:: pycon

   >>> for item in dir(net.lib):
   ...     if not item.startswith('_'):
   ...         attr = getattr(net.lib, item)
   ...         print('{} {}'.format(item, type(attr)))
   ...
   DotNetMSL <class 'CLR.ModuleObject'>
   StaticClass <class 'CLR.CLR Metatype'>
   StringManipulation <class 'CLR.CLR Metatype'>
   System <class 'CLR.ModuleObject'>

Create an instance of the ``BasicMath`` class in the ``DotNetMSL`` namespace
and call the ``multiply_doubles`` method

.. code-block:: pycon

   >>> bm = net.lib.DotNetMSL.BasicMath()
   >>> bm.multiply_doubles(2.3, 5.6)
   12.879999...

Create an instance of the ``ArrayManipulation`` class in the ``DotNetMSL``
namespace and call the ``scalar_multiply`` method

.. code-block:: pycon

   >>> am = net.lib.DotNetMSL.ArrayManipulation()
   >>> values = am.scalar_multiply(2., [1., 2., 3., 4., 5.])
   >>> values
   <System.Double[] object at ...>
   >>> [val for val in values]
   [2.0, 4.0, 6.0, 8.0, 10.0]

Use the ``reverse_string`` method in the ``StringManipulation`` class to
reverse a string

.. code-block:: pycon

   >>> net.lib.StringManipulation().reverse_string('abcdefghijklmnopqrstuvwxyz')
   'zyxwvutsrqponmlkjihgfedcba'

Use the static ``add_multiple`` method in the ``StaticClass`` class to add
five integers

.. code-block:: pycon

   >>> net.lib.StaticClass.add_multiple(1, 2, 3, 4, 5)
   15

.. _System: https://docs.microsoft.com/en-us/dotnet/api/system
