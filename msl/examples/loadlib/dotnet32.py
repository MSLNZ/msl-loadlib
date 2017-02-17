"""
A wrapper around a 32-bit .NET library using `Python for .NET <http://pythonnet.github.io/>`_.

Example of a server that loads a 32-bit .NET library, *dotnet_lib32.dll*
in a 32-bit Python interpreter to host the library. The corresponding :mod:`~.dotnet64`
module can be executed by a 64-bit Python interpreter and the :class:`~.dotnet64.DotNet64`
class can send a request to the :class:`~.dotnet32.DotNet32` class which calls the
32-bit library to execute the request and then return the response from the library.

*dotnet_lib32.dll* is a library for the `EPSON RC+ 6-axis robot
<http://www.d.umn.edu/~rlindek1/ME4135_11/e_SPEL%2BRef54_r1.pdf>`_, ``SpelNetLib``.
"""
import os

from msl.loadlib import Server32


class DotNet32(Server32):
    """
    Example of a class that is a wrapper around a 32-bit .NET Framework library,
    *dotnet_lib32.dll*.

    The objects within *dotnet_lib32.dll* can be inspected (which is what this
    example illustrates), however, it is not possible to create an instance of any
    of the ``SpelNetLib`` classes because none of the additional dependencies for
    *dotnet_lib32.dll* are available, since one would need to install the Epson RC
    software.

    Args:
        host (str): The IP address of the server.
        port (int): The port to open on the server.
        quiet (bool): Whether to hide :py:data:`sys.stdout` messages from the server.

    .. note::
        Any class that is a subclass of :class:`~msl.loadlib.server32.Server32` **MUST**
        provide three arguments in its constructor: ``host``, ``port`` and ``quiet``
        (in that order). Otherwise the ``server32_*`` executable, see
        :class:`~msl.loadlib.start_server32`, cannot create an instance of the
        :class:`~msl.loadlib.server32.Server32` subclass.
    """
    def __init__(self, host, port, quiet):
        Server32.__init__(self, os.path.join(os.path.dirname(__file__), 'dotnet_lib32.dll'),
                          'net', host, port, quiet)

    def get_module_name(self):
        """
        Returns the name of the .NET module.

        See the corresponding 64-bit :meth:`~.dotnet64.DotNet64.get_module_name` method.
        """
        return self.lib.__name__

    def get_class_names(self):
        """
        Returns the names of classes that are available in the ``SpelNetLib`` module.

        See the corresponding 64-bit :meth:`~.dotnet64.DotNet64.get_class_names` method.
        """
        return ';'.join(str(name) for name in self.net.GetExportedTypes()).split(';')

    def get_class_functions(self, cls):
        """
        Returns the names of the .NET functions that are available in a ``SpelNetLib`` class.

        See the corresponding 64-bit :meth:`~.dotnet64.DotNet64.get_class_functions` method.

        Args:
            cls (str): The name of a ``SpelNetLib`` class.
        """
        names = dir(getattr(self.lib, cls))
        return ';'.join(str(name) for name in names if not name.startswith('_')).split(';')
