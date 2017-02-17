"""
Communicates with a 32-bit .NET library via the :class:`~.dotnet32.DotNet32` class.

Example of a module that can be executed within a 64-bit Python interpreter which can
communicate with a 32-bit .NET library, *dotnet_lib32.dll* that is hosted by
a 32-bit Python server, :mod:`.dotnet32`. A 64-bit process cannot load a
32-bit library and therefore `inter-process communication <ipc_>`_ is used to
interact with a 32-bit library from a 64-bit process.

:class:`~.dotnet64.DotNet64` is the 64-bit client and :class:`~.dotnet32.DotNet32`
is the 32-bit server for `inter-process communication <ipc_>`_.

*dotnet_lib32.dll* is a library for the `EPSON RC+ 6-axis robot
<http://www.d.umn.edu/~rlindek1/ME4135_11/e_SPEL%2BRef54_r1.pdf>`_, ``SpelNetLib``.

.. _ipc: https://en.wikipedia.org/wiki/Inter-process_communication
"""
import os

from msl.loadlib import Client64


class DotNet64(Client64):
    """
    Example of a class that can communicate with a 32-bit .NET library,
    *dotnet_lib32.dll*.

    The objects within *dotnet_lib32.dll* can be inspected (which is what this example
    illustrates), however, it is not possible to create an instance of any of the
    ``SpelNetLib`` classes because none of the additional dependencies for
    *dotnet_lib32.dll* are available, since one would need to install the Epson RC
    software.
    """
    def __init__(self):
        # specify the name of the corresponding 32-bit server module, dotnet32, which hosts
        # the 32-bit .NET library -- dotnet_lib32.dll.
        Client64.__init__(self, module32='dotnet32', append_path=os.path.dirname(__file__))

    def get_module_name(self):
        """
        Request the name of the .NET module.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.get_module_name` method.
        """
        return self.request32('get_module_name')

    def get_class_names(self):
        """
        Request the names of the classes that are available in the ``SpelNetLib`` module.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.get_class_names` method.
        """
        return self.request32('get_class_names')

    def get_class_functions(self, cls):
        """
        Request the names of the functions that are available in a ``SpelNetLib`` class.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.get_class_functions` method.

        Args:
            cls (str): The name of a ``SpelNetLib`` class.
        """
        return self.request32('get_class_functions', cls=cls)


if __name__ == '__main__':

    dll = DotNet64()
    print(dll.lib32_path)
    print(dll.get_module_name())
    print(dll.get_class_names())
    print(dll.get_class_functions('Spel'))
    print(dll.get_class_functions('SpelAxis'))
