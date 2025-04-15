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
from __future__ import annotations

import os
from typing import Sequence

from msl.loadlib import Client64


class DotNet64(Client64):

    def __init__(self) -> None:
        """Communicates with the 32-bit C# :ref:`dotnet_lib32.dll <dotnet-lib>` library.

        This class demonstrates how to communicate with a 32-bit .NET library if an instance of this
        class is created within a 64-bit Python interpreter.
        """
        # specify the name of the corresponding 32-bit server module, dotnet32, which hosts
        # the 32-bit .NET library -- dotnet_lib32.dll.
        super().__init__(module32="dotnet32", append_sys_path=os.path.dirname(__file__))

    def get_class_names(self) -> list[str]:
        """Returns the class names in the library.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.get_class_names` method.

        :return: The names of the classes that are available in :ref:`dotnet_lib32.dll <dotnet-lib>`.
        """
        return self.request32("get_class_names")

    def add_integers(self, a: int, b: int) -> int:
        """Add two integers.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.add_integers` method.

        :param a: First integer.
        :param b: Second integer.
        :return: The sum of `a` and `b`.
        """
        return self.request32("add_integers", a, b)

    def divide_floats(self, a: float, b: float) -> float:
        """Divide two C# floating-point numbers.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.divide_floats` method.

        :param a: First floating-point number.
        :param b: Second floating-point number.
        :return: The quotient of `a` / `b`.
        """
        return self.request32("divide_floats", a, b)

    def multiply_doubles(self, a: float, b: float) -> float:
        """Multiply two C# double-precision numbers.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.multiply_doubles` method.

        :param a: First double-precision number.
        :param b: Second double-precision number.
        :return: The product of `a` * `b`.
        """
        return self.request32("multiply_doubles", a, b)

    def add_or_subtract(self, a: float, b: float, do_addition: bool) -> float:
        """Add or subtract two C# double-precision numbers.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.add_or_subtract` method.

        :param a: First double-precision number.
        :param b: Second double-precision number.
        :param do_addition: Whether to add or subtract the numbers.
        :return: `a+b` if `do_addition` is :data:`True` else `a-b`.
        """
        return self.request32("add_or_subtract", a, b, do_addition)

    def scalar_multiply(self, a: float, xin: Sequence[float]) -> list[float]:
        """Multiply each element in an array by a number.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.scalar_multiply` method.

        :param a: Scalar value.
        :param xin: Array to modify.
        :return: A new array with each element in `xin` multiplied by `a`.
        """
        return self.request32("scalar_multiply", a, xin)

    def multiply_matrices(self,
                          a1: Sequence[Sequence[float]],
                          a2: Sequence[Sequence[float]]) -> list[list[float]]:
        """Multiply two matrices.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.multiply_matrices` method.

        :param a1: First matrix.
        :param a2: Second matrix.
        :return: The result of `a1` * `a2`.
        """
        return self.request32("multiply_matrices", a1, a2)

    def reverse_string(self, original: str) -> str:
        """Reverse a string.

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.reverse_string` method.

        :param original: The original string.
        :return: The string reversed.
        """
        return self.request32("reverse_string", original)

    def add_multiple(self, a: int, b: int, c: int, d: int, e: int) -> int:
        """Add multiple integers. *Calls a static method in a static class.*

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.add_multiple` method.

        :param a: First integer.
        :param b: Second integer.
        :param c: Third integer.
        :param d: Fourth integer.
        :param e: Fifth integer.
        :return: The sum of the input arguments.
        """
        return self.request32("add_multiple", a, b, c, d, e)

    def concatenate(self, a: str, b: str, c: str, d: bool, e: str) -> str:
        """
        Concatenate strings. *Calls a static method in a static class.*

        See the corresponding 32-bit :meth:`~.dotnet32.DotNet32.concatenate` method.

        :param a: First string.
        :param b: Second string.
        :param c: Third string.
        :param d: Whether to include `e` in the concatenation.
        :param e: Fourth string.
        :return: The strings concatenated together.
        """
        return self.request32("concatenate", a, b, c, d, e)
