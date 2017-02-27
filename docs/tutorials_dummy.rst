.. _tutorial_dummy:

==============================================
Load a 32-bit *Dummy* library in 64-bit Python
==============================================

This example does not actually communicate with a 32-bit shared library but shows how Python data types
are preserved when they are passed from the :class:`~msl.examples.loadlib.dummy64.Dummy64` client to the
:class:`~msl.examples.loadlib.dummy32.Dummy32` server and back. The :class:`~msl.examples.loadlib.dummy32.Dummy32`
server just returns a :py:class:`tuple` of the ``args, kwargs`` that it received back to the
:class:`~msl.examples.loadlib.dummy64.Dummy64` client.

The following is a script that illustrates that the data types are preserved:

.. code-block:: python

   from msl.examples.loadlib import Dummy64

   d = Dummy64()
   d.send_data()
   d.send_data(True)

   d.send_data([1, 2, 3, 4, 5, 6])
   d.send_data(data='my string')
   d.send_data(x=[1.2, 3.4, 6.1], y=[43.2, 23.6, 12.7])
   d.send_data(1.12345, {'my list': [1, 2, 3, 4]}, 0.2j, range(10), x=True, y='hello world!')

Running this script would create the following output

.. note::
   The black text corresponds to the :class:`~msl.examples.loadlib.dummy64.Dummy64` :py:func:`print`
   statements and the red text are the :class:`~msl.examples.loadlib.dummy32.Dummy32` :py:func:`print`
   statements.

.. image:: _static/dummy_output.png

Or, by using an interactive console, create a :class:`~msl.examples.loadlib.dummy64.Dummy64` object:

.. code-block:: python

   >>> from msl.examples.loadlib import Dummy64
   >>> d = Dummy64()
   Client running on 3.5.2 |Continuum Analytics, Inc.| (default, Jul  5 2016, 11:41:13) [MSC v.1900 64 bit (AMD64)]

Send a boolean as an argument, see :meth:`~msl.examples.loadlib.dummy64.Dummy64.send_data`:

.. code-block:: python

   >>> d.send_data(True)
   Are the 64- and 32-bit arguments equal? True
       <class 'bool'> True

Send a boolean as a keyword argument, see :meth:`~msl.examples.loadlib.dummy64.Dummy64.send_data`:

.. code-block:: python

   >>> d.send_data(boolean=True)
   Are the 64- and 32-bit keyword arguments equal? True
       boolean: <class 'bool'> True

Send multiple data types as arguments and as keyword arguments, see
:meth:`~msl.examples.loadlib.dummy64.Dummy64.send_data`:

.. code-block:: python

   >>> d.send_data(1.2, {'my list':[1, 2, 3]}, 0.2j, range(10), x=True, y='hello world!')
   Are the 64- and 32-bit arguments equal? True
        <class 'float'> 1.2
        <class 'dict'> {'my list': [1, 2, 3]}
        <class 'complex'> 0.2j
        <class 'range'> range(0, 10)
   Are the 64- and 32-bit keyword arguments equal? True
       x: <class 'bool'> True
       y: <class 'str'> hello world!

Shutdown the server when you are done communicating with the 32-bit library (all of the
:py:func:`print` statements from the server get displayed once the server shuts down), see
:meth:`~msl.loadlib.client64.Client64.shutdown_server`:

.. code-block:: python

   >>> d.shutdown_server()
   Python 3.5.2 |Continuum Analytics, Inc.| (default, Jul  5 2016, 11:45:57) [MSC v.1900 32 bit (Intel)]
   Serving cpp_lib32.dll on http://127.0.0.1:2521
   The 32-bit server received these args:
        <class 'bool'> True
   The 32-bit server received these args:
        <class 'list'> [1, 2, 3, 4, 5, 6]
   The 32-bit server received these kwargs:
       data: <class 'str'> my string
   The 32-bit server received these kwargs:
       x: <class 'list'> [1.2, 3.4, 6.1]
       y: <class 'list'> [43.2, 23.6, 12.7]
   The 32-bit server received these args:
        <class 'float'> 1.12345
        <class 'dict'> {'my list': [1, 2, 3, 4]}
        <class 'complex'> 0.2j
        <class 'range'> range(0, 10)
   The 32-bit server received these kwargs:
       x: <class 'bool'> True
       y: <class 'str'> hello world!
   Stopped http://127.0.0.1:2521

.. note::
   The server will automatically shutdown when the :class:`~msl.examples.loadlib.dummy64.Dummy64`
   object gets destroyed (as it did in the example script above). When using a subclass of
   :class:`~msl.loadlib.client64.Client64` in a script, the `__del__ <del_>`_ command gets
   called automatically when the instance is about to be destroyed and therefore you do not have to
   call the :meth:`~msl.loadlib.client64.Client64.shutdown_server` method to shutdown the server.
   If the :class:`~msl.loadlib.client64.Client64` subclass does not get destroyed properly, for
   example if you are using an interactive console and then exit the console abruptly, then the server
   will still be running and therefore you must manually terminate the server processes (two
   ``server32-*`` processes are created when the server starts).

.. _del: https://docs.python.org/3/reference/datamodel.html#object.__del__
