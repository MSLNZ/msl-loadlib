"""
An example of a 32-bit *echo* server.

Example of a server that is executed by a 32-bit Python interpreter that receives
requests from the corresponding :mod:`~.echo64` module which can be run by a 64-bit
Python interpreter.

:class:`~.echo32.Echo32` is the 32-bit server class and :class:`~.echo64.Echo64` is
the 64-bit client class. These *echo* classes do not actually communicate with a shared
library. The point of these *echo* classes is to show that a Python data type in a
64-bit process appears as the same data type in the 32-bit process and vice versa.
"""
import os

from msl.loadlib import Server32


class Echo32(Server32):
    """
    Example of a server class that illustrates that Python data types are preserved
    when they are sent from the :class:`~.echo64.Echo64` client to the server.

    Parameters
    ----------
    host : :class:`str`
        The IP address of the server.
    port : :class:`int`
        The port to open on the server.
    quiet : :class:`bool`
        Whether to hide :data:`sys.stdout` messages from the server.

    Note
    ----
    Any class that is a subclass of :class:`~msl.loadlib.server32.Server32` **MUST**
    provide three arguments in its constructor: `host`, `port` and `quiet`
    (in that order) and `**kwargs`. Otherwise the ``server32`` executable, see
    :class:`~msl.loadlib.start_server32`, cannot create an instance of the
    :class:`~msl.loadlib.server32.Server32` subclass.
    """
    def __init__(self, host, port, quiet, **kwargs):
        # even though this is a *echo* class that does not call a shared library
        # we still need to provide a library file that exists. Use the C++ library.
        super(Echo32, self).__init__(os.path.join(os.path.dirname(__file__), 'cpp_lib32'),
                                     'cdll', host, port, quiet)

    def received_data(self, *args, **kwargs):
        """Process a request from the :meth:`~.echo64.Echo64.send_data` method from
        the 64-bit client.

        Parameters
        ----------
        *args
            The arguments.
        **kwargs
            The keyword arguments.

        Returns
        -------
        :class:`tuple`
            The `args` and `kwargs` that were received.
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
