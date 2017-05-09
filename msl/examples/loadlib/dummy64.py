"""
A *dummy* example of a 64-bit client.

Example of a client that can be executed by a 64-bit Python interpreter that sends
requests to the corresponding :mod:`.dummy32` module which is executed by a
32-bit Python interpreter.

:class:`~.dummy32.Dummy32` is the 32-bit server class and :class:`~.dummy64.Dummy64` is
the 64-bit client class. These *dummy* classes do not actually communicate with a shared
library. The point of these *dummy* classes is to show that a Python data type in a
64-bit process appears as the same data type in the 32-bit process and vice versa.
"""
import os
import sys

from msl.loadlib import Client64


class Dummy64(Client64):
    """
    Example of a client class that illustrates that Python data types are
    preserved when they are sent to the :class:`~.dummy32.Dummy32` server
    and back again.

    Parameters
    ----------
    quiet : :obj:`bool`, optional
        Whether to hide :obj:`sys.stdout` messages from the client and from the server.
    """
    def __init__(self, quiet=False):
        Client64.__init__(self, module32='dummy32', append_sys_path=os.path.dirname(__file__), quiet=quiet)

        self._quiet = quiet
        if not quiet:
            print('Client running on ' + sys.version)

    def send_data(self, *args, **kwargs):
        """Send a request to execute the :meth:`~.dummy32.Dummy32.received_data`
        method on the 32-bit server.

        Parameters
        ----------
        *args
            The arguments that the :meth:`~.dummy32.Dummy32.received_data` method requires.
        **kwargs
            The keyword arguments that the :meth:`~.dummy32.Dummy32.received_data` method requires.
        
        Returns
        -------
        :obj:`tuple`
            The `args` and `kwargs` that were returned from :meth:`~.dummy32.Dummy32.received_data`.
        """
        args32, kwargs32 = self.request32('received_data', *args, **kwargs)
        if args and not self._quiet:
            print('Are the 64- and 32-bit arguments equal? {}'.format(args == args32))
            for arg in args32:
                print('\t{} {}'.format(type(arg), arg))
        if kwargs and not self._quiet:
            print('Are the 64- and 32-bit keyword arguments equal? {}'.format(kwargs == kwargs32))
            for key, value in kwargs32.items():
                print('\t{}: {} {}'.format(key, type(value), value))
        return args32, kwargs32


if __name__ == '__main__':

    d = Dummy64()
    d.send_data()
    d.send_data(True)

    d.send_data([1, 2, 3, 4, 5, 6])
    d.send_data(data='my string')
    d.send_data(x=[1.2, 3.4, 6.1], y=[43.2, 23.6, 12.7])
    d.send_data(1.12345, {'my list': [1, 2, 3, 4]}, 0.2j, range(10), x=True, y='hello world!')
