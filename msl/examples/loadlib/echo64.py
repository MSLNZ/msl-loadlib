"""
An example of a 64-bit *echo* client.

Example of a client that can be executed by a 64-bit Python interpreter that sends
requests to the corresponding :mod:`.echo32` module which is executed by a
32-bit Python interpreter.

:class:`~.echo32.Echo32` is the 32-bit server class and :class:`~.echo64.Echo64` is
the 64-bit client class. These *echo* classes do not actually communicate with a shared
library. The point of these *echo* classes is to show that a Python data type in a
64-bit process appears as the same data type in the 32-bit process and vice versa.
"""
import os

from msl.loadlib import Client64


class Echo64(Client64):

    def __init__(self):
        """
        Example of a client class that illustrates that Python data types are
        preserved when they are sent to the :class:`~.echo32.Echo32` server
        and back again.
        """
        super(Echo64, self).__init__(module32='echo32', append_sys_path=os.path.dirname(__file__))

    def send_data(self, *args, **kwargs):
        """Send a request to execute the :meth:`~.echo32.Echo32.received_data`
        method on the 32-bit server.

        Parameters
        ----------
        *args
            The arguments that the :meth:`~.echo32.Echo32.received_data` method requires.
        **kwargs
            The keyword arguments that the :meth:`~.echo32.Echo32.received_data` method requires.
        
        Returns
        -------
        :class:`tuple`
            The `args` and `kwargs` that were returned from :meth:`~.echo32.Echo32.received_data`.
        """
        return self.request32('received_data', *args, **kwargs)
