"""Communicates with the [fortran_lib][fortran-lib] library via the [Fortran32][] class that is running on a server."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from msl.loadlib import Client64

if TYPE_CHECKING:
    from collections.abc import Sequence


class Fortran64(Client64):
    """Communicates with a 32-bit FORTRAN library."""

    def __init__(self) -> None:
        """Communicates with the 32-bit .NET [fortran_lib][fortran-lib] library.

        This class demonstrates how to communicate with a 32-bit FORTRAN library if an
        instance of this class is created within a 64-bit Python interpreter.
        """
        # specify the name of the corresponding 32-bit server module, fortran32, which hosts
        # the 32-bit FORTRAN library -- fortran_lib32.
        super().__init__(module32="fortran32", append_sys_path=Path(__file__).parent)

    def sum_8bit(self, a: int, b: int) -> int:
        """Send a request to add two 8-bit signed integers.

        See the corresponding [Fortran32.sum_8bit][msl.examples.loadlib.fortran32.Fortran32.sum_8bit] method.

        Args:
            a: First 8-bit signed integer.
            b: Second 8-bit signed integer.

        Returns:
            The sum, `a + b`.
        """
        reply: int = self.request32("sum_8bit", a, b)
        return reply

    def sum_16bit(self, a: int, b: int) -> int:
        """Send a request to add two 16-bit signed integers.

        See the corresponding [Fortran32.sum_16bit][msl.examples.loadlib.fortran32.Fortran32.sum_16bit] method.

        Args:
            a: First 16-bit signed integer.
            b: Second 16-bit signed integer.

        Returns:
            The sum, `a + b`.
        """
        reply: int = self.request32("sum_16bit", a, b)
        return reply

    def sum_32bit(self, a: int, b: int) -> int:
        """Send a request to add two 32-bit signed integers.

        See the corresponding [Fortran32.sum_32bit][msl.examples.loadlib.fortran32.Fortran32.sum_32bit] method.

        Args:
            a: First 32-bit signed integer.
            b: Second 32-bit signed integer.

        Returns:
            The sum, `a + b`.
        """
        reply: int = self.request32("sum_32bit", a, b)
        return reply

    def sum_64bit(self, a: int, b: int) -> int:
        """Send a request to add two 64-bit signed integers.

        See the corresponding [Fortran32.sum_64bit][msl.examples.loadlib.fortran32.Fortran32.sum_64bit] method.

        Args:
            a: First 64-bit signed integer.
            b: Second 64-bit signed integer.

        Returns:
            The sum, `a + b`.
        """
        reply: int = self.request32("sum_64bit", a, b)
        return reply

    def multiply_float32(self, a: float, b: float) -> float:
        """Send a request to multiply two FORTRAN floating-point numbers.

        See the corresponding [Fortran32.multiply_float32][msl.examples.loadlib.fortran32.Fortran32.multiply_float32]
        method.

        Args:
            a: First floating-point number.
            b: Second floating-point number.

        Returns:
            The product, `a * b`.
        """
        reply: float = self.request32("multiply_float32", a, b)
        return reply

    def multiply_float64(self, a: float, b: float) -> float:
        """Send a request to multiply two FORTRAN double-precision numbers.

        See the corresponding [Fortran32.multiply_float64][msl.examples.loadlib.fortran32.Fortran32.multiply_float64]
        method.

        Args:
            a: First double-precision number.
            b: Second double-precision number.

        Returns:
            The product, `a * b`.
        """
        reply: float = self.request32("multiply_float64", a, b)
        return reply

    def is_positive(self, a: float) -> bool:
        """Returns whether the value of the input argument is > 0.

        See the corresponding [Fortran32.is_positive][msl.examples.loadlib.fortran32.Fortran32.is_positive] method.

        Args:
            a: Double-precision number.

        Returns:
            Whether the value of `a` is &gt; 0.
        """
        reply: bool = self.request32("is_positive", a)
        return reply

    def add_or_subtract(self, a: int, b: int, *, do_addition: bool) -> int:
        """Add or subtract two integers.

        See the corresponding [Fortran32.add_or_subtract][msl.examples.loadlib.fortran32.Fortran32.add_or_subtract]
        method.

        Args:
            a: First integer.
            b: Second integer.
            do_addition: Whether to add or subtract the numbers.

        Returns:
            `a + b` if `do_addition` is `True` else `a - b`.
        """
        reply: int = self.request32("add_or_subtract", a, b, do_addition=do_addition)
        return reply

    def factorial(self, n: int) -> float:
        """Compute the n'th factorial.

        See the corresponding [Fortran32.factorial][msl.examples.loadlib.fortran32.Fortran32.factorial] method.

        Args:
            n: The integer to computer the factorial of. The maximum allowed value is 127.

        Returns:
            The factorial of `n`.
        """
        reply: float = self.request32("factorial", n)
        return reply

    def standard_deviation(self, data: Sequence[float]) -> float:
        """Compute the standard deviation.

        See the corresponding
        [Fortran32.standard_deviation][msl.examples.loadlib.fortran32.Fortran32.standard_deviation]
        method.

        Args:
            data: The values to compute the standard deviation of.

        Returns:
            The standard deviation of `data`.
        """
        reply: float = self.request32("standard_deviation", data)
        return reply

    def besselJ0(self, x: float) -> float:  # noqa: N802
        """Compute the Bessel function of the first kind of order 0 of x.

        See the corresponding [Fortran32.besselJ0][msl.examples.loadlib.fortran32.Fortran32.besselJ0] method.

        Args:
            x: The value to compute `BESSEL_J0` of.

        Returns:
            The value of `BESSEL_J0(x)`.
        """
        reply: float = self.request32("besselJ0", x)
        return reply

    def reverse_string(self, original: str) -> str:
        """Reverse a string.

        See the corresponding [Fortran32.reverse_string][msl.examples.loadlib.fortran32.Fortran32.reverse_string]
        method.

        Args:
            original: The original string.

        Returns:
            The string reversed.
        """
        reply: str = self.request32("reverse_string", original)
        return reply

    def add_1d_arrays(self, a1: Sequence[float], a2: Sequence[float]) -> list[float]:
        """Perform an element-wise addition of two 1D double-precision arrays.

        See the corresponding [Fortran32.add_1d_arrays][msl.examples.loadlib.fortran32.Fortran32.add_1d_arrays] method.

        Args:
            a1: First array.
            a2: Second array.

        Returns:
            The element-wise addition of `a1 + a2`.
        """
        reply: list[float] = self.request32("add_1d_arrays", a1, a2)
        return reply

    def matrix_multiply(self, a1: Sequence[Sequence[float]], a2: Sequence[Sequence[float]]) -> list[list[float]]:
        """Multiply two matrices.

        See the corresponding [Fortran32.matrix_multiply][msl.examples.loadlib.fortran32.Fortran32.matrix_multiply]
        method.

        Args:
            a1: First matrix.
            a2: Second matrix.

        Returns:
            The product, `a1 @ a2`.
        """
        reply: list[list[float]] = self.request32("matrix_multiply", a1, a2)
        return reply
