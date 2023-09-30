.. _tutorial_echo:

=================
An *Echo* Example
=================

This example illustrates that Python data types are preserved when they are
passed from the :class:`~msl.examples.loadlib.echo64.Echo64` client to the
:class:`~msl.examples.loadlib.echo32.Echo32` server and back. The
:class:`~msl.examples.loadlib.echo32.Echo32` server just returns a
:class:`tuple` of the ``(args, kwargs)`` that it received back to the
:class:`~msl.examples.loadlib.echo64.Echo64` client.

Create an :class:`~msl.examples.loadlib.echo64.Echo64` object

.. invisible-code-block: pycon

   >>> SKIP_IF_MACOS()

.. code-block:: pycon

   >>> from msl.examples.loadlib import Echo64
   >>> echo = Echo64()

send a boolean as an argument, see :meth:`~msl.examples.loadlib.echo64.Echo64.send_data`

.. code-block:: pycon

   >>> echo.send_data(True)
   ((True,), {})

send a boolean as a keyword argument

.. code-block:: pycon

   >>> echo.send_data(boolean=True)
   ((), {'boolean': True})

send multiple data types as arguments and as keyword arguments

.. code-block:: pycon

   >>> echo.send_data(1.2, {'my_list':[1, 2, 3]}, 0.2j, range(10), x=True, y='hello world!')
   ((1.2, {'my_list': [1, 2, 3]}, 0.2j, range(0, 10)), {'x': True, 'y': 'hello world!'})

Shutdown the 32-bit server when you are done

.. code-block:: pycon

   >>> stdout, stderr = echo.shutdown_server32()
