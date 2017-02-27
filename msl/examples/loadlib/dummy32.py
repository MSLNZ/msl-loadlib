"""
A *dummy* example of a 32-bit server.

Example of a server that is executed by a 32-bit Python interpreter that receives
requests from the corresponding :mod:`~.dummy64` module which can be run by a 64-bit
Python interpreter.

:class:`~.dummy32.Dummy32` is the 32-bit server class and :class:`~.dummy64.Dummy64` is
the 64-bit client class. These *dummy* classes do not actually communicate with a shared
library. The point of these *dummy* classes is to show that a Python data type in a
64-bit process appears as the same data type in the 32-bit process and vice versa.
"""
import os

from msl.loadlib import Server32


class Dummy32(Server32):
    """
    Example of a server class that illustrates that Python data types are preserved
    when they are sent from the :class:`~.dummy64.Dummy64` client to the server.

    Args:
        host (str): The IP address of the server.
        port (int): The port to open on the server.
        quiet (bool): Whether to hide :py:data:`sys.stdout` messages from the server.

    .. note::
        Any class that is a subclass of :class:`~msl.loadlib.server32.Server32` **MUST**
        provide three arguments in its constructor: ``host``, ``port`` and ``quiet``
        (in that order). Otherwise the ``server32-*`` executable, see
        :class:`~msl.loadlib.start_server32`, cannot create an instance of the
        :class:`~msl.loadlib.server32.Server32` subclass.
    """
    def __init__(self, host, port, quiet):
        # even though this is a *dummy* class that does not call a shared library
        # we still need to provide a library file that exists. Use the C++ library.
        Server32.__init__(self, os.path.join(os.path.dirname(__file__), 'cpp_lib32'),
                          'cdll', host, port, quiet)

    def received_data(self, *args, **kwargs):
        """
        Process a request from the :meth:`~.dummy64.Dummy64.send_data` method from
        the 64-bit client.

        Args:
            *args: The arguments.

            **kwargs: The keyword arguments.

        Returns:
            :py:class:`tuple`: The ``args`` and ``kwargs`` that were received.
        """
        if args and not self.quiet:
            print('The 32-bit server received these args:')
            for arg in args:
                print('\t{} {}'.format(type(arg), arg))
        if kwargs and not self.quiet:
            print('The 32-bit server received these kwargs:')
            for key, value in kwargs.items():
                print('\t{}: {} {}'.format(key, type(value), value))
        return args, kwargs
