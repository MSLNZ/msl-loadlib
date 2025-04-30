"""Communicates with the [dotnet_lib32][dotnet-lib] library via the [DotNet32][] class that is running on a server."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from msl.loadlib import Client64

if TYPE_CHECKING:
    from collections.abc import Sequence


class DotNet64(Client64):
    """Communicates with a 32-bit .NET library."""

    def __init__(self) -> None:
        """Communicates with the 32-bit .NET [dotnet_lib32.dll][dotnet-lib] library.

        This class demonstrates how to communicate with a 32-bit .NET library if an
        instance of this class is created within a 64-bit Python interpreter.
        """
        # specify the name of the corresponding 32-bit server module, dotnet32, which hosts
        # the 32-bit .NET library -- dotnet_lib32.dll.
        super().__init__("dotnet32", append_sys_path=Path(__file__).parent)

    def get_class_names(self) -> list[str]:
        """Gets the class names in the library.

        Calls [GetTypes](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.assembly.gettypes){:target="_blank"}
        using the [assembly][msl.loadlib.load_library.LoadLibrary.assembly] property.

        See the corresponding [DotNet32.get_class_names][msl.examples.loadlib.dotnet32.DotNet32.get_class_names] method.

        Returns:
            The names of the classes that are available in [dotnet_lib32.dll][dotnet-lib].
        """
        reply: list[str] = self.request32("get_class_names")
        return reply

    def add_integers(self, a: int, b: int) -> int:
        """Add two integers.

        See the corresponding [DotNet32.add_integers][msl.examples.loadlib.dotnet32.DotNet32.add_integers] method.

        Args:
            a: First integer.
            b: Second integer.

        Returns:
            The sum, `a + b`.
        """
        reply: int = self.request32("add_integers", a, b)
        return reply

    def divide_floats(self, a: float, b: float) -> float:
        """Divide two C# floating-point numbers.

        See the corresponding [DotNet32.divide_floats][msl.examples.loadlib.dotnet32.DotNet32.divide_floats] method.

        Args:
            a: The numerator.
            b: The denominator.

        Returns:
            The quotient, `a / b`.
        """
        reply: float = self.request32("divide_floats", a, b)
        return reply

    def multiply_doubles(self, a: float, b: float) -> float:
        """Multiply two C# double-precision numbers.

        See the corresponding [DotNet32.multiply_doubles][msl.examples.loadlib.dotnet32.DotNet32.multiply_doubles]
        method.

        Args:
            a: First double-precision number.
            b: Second double-precision number.

        Returns:
            The product, `a * b`.
        """
        reply: float = self.request32("multiply_doubles", a, b)
        return reply

    def add_or_subtract(self, a: float, b: float, *, do_addition: bool) -> float:
        """Add or subtract two C# double-precision numbers.

        See the corresponding [DotNet32.add_or_subtract][msl.examples.loadlib.dotnet32.DotNet32.add_or_subtract] method.

        Args:
            a: First double-precision number.
            b: Second double-precision number.
            do_addition: Whether to add or subtract the numbers.

        Returns:
            `a + b` if `do_addition` is `True` else `a - b`.
        """
        reply: float = self.request32("add_or_subtract", a, b, do_addition=do_addition)
        return reply

    def scalar_multiply(self, a: float, xin: Sequence[float]) -> list[float]:
        """Multiply each element in an array by a number.

        See the corresponding [DotNet32.scalar_multiply][msl.examples.loadlib.dotnet32.DotNet32.scalar_multiply] method.

        Args:
            a: Scalar value.
            xin: Array to modify.

        Returns:
            A new array with each element in `xin` multiplied by `a`.
        """
        reply: list[float] = self.request32("scalar_multiply", a, xin)
        return reply

    def multiply_matrices(self, a1: Sequence[Sequence[float]], a2: Sequence[Sequence[float]]) -> list[list[float]]:
        """Multiply two matrices.

        See the corresponding [DotNet32.multiply_matrices][msl.examples.loadlib.dotnet32.DotNet32.multiply_matrices]
        method.

        Args:
            a1: First matrix.
            a2: Second matrix.

        Return:
            The product, `a1 @ a2`.
        """
        reply: list[list[float]] = self.request32("multiply_matrices", a1, a2)
        return reply

    def reverse_string(self, original: str) -> str:
        """Reverse a string.

        See the corresponding [DotNet32.reverse_string][msl.examples.loadlib.dotnet32.DotNet32.reverse_string] method.

        Args:
            original: The original string.

        Returns:
            The string reversed.
        """
        reply: str = self.request32("reverse_string", original)
        return reply

    def add_multiple(self, a: int, b: int, c: int, d: int, e: int) -> int:
        """Add multiple integers.

        Calls a static method in a static class.

        See the corresponding [DotNet32.add_multiple][msl.examples.loadlib.dotnet32.DotNet32.add_multiple] method.

        Args:
            a: First integer.
            b: Second integer.
            c: Third integer.
            d: Fourth integer.
            e: Fifth integer.

        Returns:
            The sum of the input arguments.
        """
        reply: int = self.request32("add_multiple", a, b, c, d, e)
        return reply

    def concatenate(self, a: str, b: str, c: str, d: bool, e: str) -> str:  # noqa: FBT001
        """Concatenate strings.

        Calls a static method in a static class.

        See the corresponding [DotNet32.concatenate][msl.examples.loadlib.dotnet32.DotNet32.concatenate] method.

        Args:
            a: First string.
            b: Second string.
            c: Third string.
            d: Whether to include `e` in the concatenation.
            e: Fourth string.

        Returns:
            The strings concatenated together.
        """
        reply: str = self.request32("concatenate", a, b, c, d, e)
        return reply
