.. _tutorial_echo:

=================
An *Echo* Example
=================

This example illustrates how Python data types are preserved when they are passed from the
:class:`~msl.examples.loadlib.echo64.Echo64` client to the :class:`~msl.examples.loadlib.echo32.Echo32`
server and back. The :class:`~msl.examples.loadlib.echo32.Echo32`
server just returns a :class:`tuple` of the ``(args, kwargs)`` that it received back to the
:class:`~msl.examples.loadlib.echo64.Echo64` client.

Create an :class:`~msl.examples.loadlib.echo64.Echo64` object

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

and, send multiple data types as arguments and as keyword arguments

.. code-block:: pycon

   >>> echo.send_data(1.2, {'my_list':[1, 2, 3]}, 0.2j, range(10), x=True, y='hello world!')
   ((1.2, {'my_list': [1, 2, 3]}, 0.2j, range(0, 10)), {'x': True, 'y': 'hello world!'})

Shutdown the 32-bit server when you are done communicating with the 32-bit library
(the *stdout* and *stderr* streams from the 32-bit server are returned), see
:meth:`~msl.loadlib.client64.Client64.shutdown_server32`

.. code-block:: pycon

   >>> stdout, stderr = echo.shutdown_server32()
   >>> print(stdout.read().decode())
   Python 3.7.7 (tags/v3.7.7:d7c567b08f, Mar 10 2020, 09:44:33) [MSC v.1900 32 bit (Intel)]
   Serving 'cpp_lib32.dll' on http://127.0.0.1:52666
   Stopped http://127.0.0.1:52666

You will notice that the *stdout* stream from the 32-bit server indicated that it is
*Serving cpp_lib32.dll on http://127.0.0.1:52666*. Even though this is an *echo* example,
a library must still be loaded even though it is not being called. The *cpp_lib32.dll*
library is loaded to satisfy this requirement.

.. note::
   The server will automatically shutdown when the :class:`~msl.examples.loadlib.echo64.Echo64`
   object gets destroyed (as it did in the example script above). When using a subclass of
   :class:`~msl.loadlib.client64.Client64` in a script, the :meth:`__del__ <object.__del__>` method
   gets called automatically when the instance is about to be destroyed (and the reference count
   reaches 0) and therefore you do not have to call the
   :meth:`~msl.loadlib.client64.Client64.shutdown_server32` method to shutdown the server.
   If the :class:`~msl.loadlib.client64.Client64` subclass does not get destroyed properly, for
   example if you are using an interactive console and then exit the console abruptly, then the server
   will still be running and therefore you must manually terminate the server processes.
