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
    """Communicates with the 32-bit C# :ref:`dotnet_lib32.dll <dotnet-lib>` library.

    This class demonstrates how to communicate with a 32-bit .NET library if an instance of this
    class is created within a 64-bit Python interpreter.
    """
    def __init__(self):
        # specify the name of the corresponding 32-bit server module, dotnet32, which hosts
        # the 32-bit .NET library -- dotnet_lib32.dll.
        super(DotNet64, self).__init__(module32='dotnet32', append_sys_path=os.path.dirname(__file__))

    def get_class_names(self):
        """Return the class names in the library.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.get_class_names` method.

        Returns
        -------
        :class:`list` of :class:`str`
            The names of the classes that are available in :ref:`dotnet_lib32.dll <dotnet-lib>`.        
        """
        return self.request32('get_class_names')

    def add_integers(self, a, b):
        """Add two integers.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.add_integers` method.

        Parameters
        ----------
        a : :class:`int`
            The first integer.
        b : :class:`int`
            The second integer.

        Returns
        -------
        :class:`int`
            The sum of `a` and `b`.
        """
        return self.request32('add_integers', a, b)

    def divide_floats(self, a, b):
        """Divide two C# floating-point numbers.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.divide_floats` method.

        Parameters
        ----------
        a : :class:`float`
            The first number.
        b : :class:`float`
            The second number.

        Returns
        -------
        :class:`float`:
            The quotient of `a` / `b`.
        """
        return self.request32('divide_floats', a, b)

    def multiply_doubles(self, a, b):
        """Multiply two C# double-precision numbers.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.multiply_doubles` method.

        Parameters
        ----------
        a : :class:`float`
            The first number.
        b : :class:`float`
            The second number.

        Returns
        -------
        :class:`float`
            The product of `a` * `b`.
        """
        return self.request32('multiply_doubles', a, b)

    def add_or_subtract(self, a, b, do_addition):
        """Add or subtract two C# double-precision numbers.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.add_or_subtract` method.

        Parameters
        ----------
        a : :class:`float`
            The first double-precision number.
        b : :class:`float`
            The second double-precision number.
        do_addition : :class:`bool`
            Whether to **add** the numbers.

        Returns
        -------
        :class:`float`
            Either `a` + `b` if `do_addition` is :data:`True` else `a` - `b`.
        """
        return self.request32('add_or_subtract', a, b, do_addition)

    def scalar_multiply(self, a, xin):
        """Multiply each element in an array by a number.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.scalar_multiply` method.

        Parameters
        ----------
        a : :class:`float`
            The scalar value.
        xin : :class:`list` of :class:`float`
            The array to modify.

        Returns
        -------
        :class:`list` of :class:`float`
            A new array with each element in `xin` multiplied by `a`.
        """
        return self.request32('scalar_multiply', a, xin)

    def multiply_matrices(self, a1, a2):
        """Multiply two matrices.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.multiply_matrices` method.

        Parameters
        ----------
        a1 : :class:`list` of :class:`list` of :class:`float`
            The first matrix.
        a2 : :class:`list` of :class:`list` of :class:`float`
            The second matrix.

        Returns
        -------
        :class:`list` of :class:`list` of :class:`float`
             The result of `a1` * `a2`.
        """
        return self.request32('multiply_matrices', a1, a2)

    def reverse_string(self, original):
        """Reverse a string.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.reverse_string` method.

        Parameters
        ----------
        original : :class:`str`
            The original string.

        Returns
        -------
        :class:`str`
            The string reversed.
        """
        return self.request32('reverse_string', original)

    def add_multiple(self, a, b, c, d, e):
        """Add multiple integers. *Calls a static method in a static class.*

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.add_multiple` method.

        Parameters
        ----------
        a : :class:`int`
            An integer.
        b : :class:`int`
            An integer.
        c : :class:`int`
            An integer.
        d : :class:`int`
            An integer.
        e : :class:`int`
            An integer.

        Returns
        -------
        :class:`int`
            The sum of the input arguments.
        """
        return self.request32('add_multiple', a, b, c, d, e)

    def concatenate(self, a, b, c, d, e):
        """
        Concatenate strings. *Calls a static method in a static class.*

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.concatenate` method.

        Parameters
        ----------
        a : :class:`str`
            A string.
        b : :class:`str`
            A string.
        c : :class:`str`
            A string.
        d : :class:`bool`
            Whether to include `e` in the concatenation.
        e : :class:`str`
            A string.

        Returns
        -------
        :class:`str`
            The strings concatenated together.
        """
        return self.request32('concatenate', a, b, c, d, e)
