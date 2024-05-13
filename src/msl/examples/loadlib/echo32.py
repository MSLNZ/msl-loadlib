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
from __future__ import annotations

import os
from typing import Any

from msl.loadlib import Server32


class Echo32(Server32):

    def __init__(self, host: str, port: int, **kwargs: str) -> None:
        """
        Example of a server class that illustrates that Python data types are preserved
        when they are sent from the :class:`~.echo64.Echo64` client to the server.

        :param host: The IP address (or hostname) to use for the server.
        :param port: The port to open for the server.
        :param kwargs: Optional keyword arguments. The keys and values are of type :class:`str`.
        """
        # even though this is a *echo* class that does not call a shared library
        # we still need to provide a library file that exists. Use the C++ library.
        path = os.path.join(os.path.dirname(__file__), 'cpp_lib32')
        super().__init__(path, 'cdll', host, port)

    @staticmethod
    def received_data(*args: Any, **kwargs: Any) -> tuple[tuple[Any, ...], dict[Any, Any]]:
        """Process a request from the :meth:`~.echo64.Echo64.send_data` method from
        the 64-bit client.

        :param args: The arguments.
        :param kwargs: The keyword arguments.
        :return: The `args` and `kwargs` that were received.
        """
        return args, kwargs
