"""
Communicates with a 32-bit .NET library via the :class:`~.dotnet32.DotNet32` class.

Example of a module that can be executed within a 64-bit Python interpreter which can
communicate with a 32-bit .NET library, :ref:`dotnet_lib32.dll <dotnet-lib>` that is
hosted by a 32-bit Python server, :mod:`.dotnet32`. A 64-bit process cannot load a
32-bit library and therefore `inter-process communication <ipc_>`_ is used to
interact with a 32-bit library from a 64-bit process.

:class:`~.dotnet64.DotNet64` is the 64-bit client and :class:`~.dotnet32.DotNet32`
is the 32-bit server for `inter-process communication <ipc_>`_.

.. _ipc: https://en.wikipedia.org/wiki/Inter-process_communication
"""
import os

from msl.loadlib import Client64


class DotNet64(Client64):
    """
    Communicates with the 32-bit C# :ref:`dotnet_lib32.dll <dotnet-lib>` library.

    This class demonstrates how to communicate with a 32-bit .NET library if an instance of this
    class is created within a 64-bit Python interpreter.
    """
    def __init__(self):
        # specify the name of the corresponding 32-bit server module, dotnet32, which hosts
        # the 32-bit .NET library -- dotnet_lib32.dll.
        Client64.__init__(self, module32='dotnet32', append_path=os.path.dirname(__file__))

    def get_class_names(self):
        """
        Request the names of the classes that are available in :ref:`dotnet_lib32.dll <dotnet-lib>`.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.get_class_names` method.
        """
        return self.request32('get_class_names')

    def add_integers(self, a, b):
        """
        Add two integers.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.add_integers` method.

        Args:
            a (int): The first integer.
            b (int): The second integer.

        Returns:
            :py:class:`int`: The sum of ``a`` and ``b``.
        """
        return self.request32('add_integers', a, b)

    def divide_floats(self, a, b):
        """
        Divide two C# floating-point numbers.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.divide_floats` method.

        Args:
            a (float): The first number.
            b (float): The second number.

        Returns:
            :py:class:`float`:  ``a`` / ``b``.
        """
        return self.request32('divide_floats', a, b)

    def multiply_doubles(self, a, b):
        """
        Multiply two C# double-precision numbers.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.multiply_doubles` method.

        Args:
            a (float): The first number.
            b (float): The second number.

        Returns:
            :py:class:`float`:  ``a`` * ``b``.
        """
        return self.request32('multiply_doubles', a, b)

    def add_or_subtract(self, a, b, do_addition):
        """
        Add or subtract two C# double-precision numbers.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.add_or_subtract` method.

        Args:
            a (float): The first double-precision number.
            b (float): The second double-precision number.
            do_addition (bool): Whether to **add**, :py:data:`True`, or **subtract**,
                :py:data:`False`, the numbers.

        Returns:
            :py:class:`float`: Either ``a`` + ``b`` if ``do_addition`` is
            :py:data:`True` or ``a`` - ``b`` otherwise.
        """
        return self.request32('add_or_subtract', a, b, do_addition)

    def scalar_multiply(self, a, xin):
        """
        Multiply each element in an array by a number.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.scalar_multiply` method.

        Args:
            a (float): The scalar value.
            xin (list[float]): The array to modify.

        Returns:
            A :py:class:`list` of :py:class:`float`'s: A new array with each
            element in ``xin`` multiplied by ``a``.
        """
        return self.request32('scalar_multiply', a, xin)

    def multiply_matrices(self, a1, a2):
        """
        Multiply two matrices.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.multiply_matrices` method.

        Args:
            a1 (list[list[float]]): A matrix.
            a2 (list[list[float]]): A matrix.

        Returns:
             The result of ``a1`` * ``a2``.
        """
        return self.request32('multiply_matrices', a1, a2)

    def reverse_string(self, original):
        """
        Reverse a string.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.reverse_string` method.

        Args:
            original (str): The original string.

        Returns:
            :py:class:`str`: The string reversed.
        """
        return self.request32('reverse_string', original)

    def add_multiple(self, a, b, c, d, e):
        """
        Add multiple integers. *Calls a static method in a static class.*

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.add_multiple` method.

        Args:
            a (int): An integer.
            b (int): An integer.
            c (int): An integer.
            d (int): An integer.
            e (int): An integer.

        Returns:
            :py:class:`int`: The sum of input arguments.
        """
        return self.request32('add_multiple', a, b, c, d, e)

    def concatenate(self, a, b, c, d, e):
        """
        Concatenate strings. *Calls a static method in a static class.*

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.concatenate` method.

        Args:
            a (str): A string
            b (str): A string
            c (str): A string
            d (bool): A boolean value for whether to include ``e`` in the concatenation
            e (str): A string

        Returns:
            :py:class:`str`: The strings concatenated together.
        """
        return self.request32('concatenate', a, b, c, d, e)


if __name__ == '__main__':

    dll = DotNet64()
    print(dll.lib32_path)
    print(dll.get_class_names())
    print(dll.add_integers(4, 5))
    print(dll.divide_floats(4., 5.))
    print(dll.multiply_doubles(872.24, 525.525))
    print(dll.add_or_subtract(99., 9., True))
    print(dll.add_or_subtract(99., 9., False))
    print(dll.scalar_multiply(2., [float(val) for val in range(10)]))
    print(dll.multiply_matrices([[1., 2., 3.], [4., 5., 6.]], [[1., 2.], [3., 4.], [5., 6.]]))
    print(dll.reverse_string('New Zealand'))
    print(dll.add_multiple(1, 2, 3, 4, 5))
    print(dll.concatenate('the ', 'experiment ', 'worked ', False, 'temporarily'))
    print(dll.concatenate('the ', 'experiment ', 'worked ', True, 'temporarily'))
