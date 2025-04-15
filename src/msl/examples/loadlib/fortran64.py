"""
Communicates with :ref:`fortran_lib32 <fortran-lib>` via the :class:`~.fortran32.Fortran32`
class.

Example of a module that can be executed within a 64-bit Python interpreter which can
communicate with a 32-bit library, :ref:`fortran_lib32 <fortran-lib>`, that is hosted
by a 32-bit Python server, :mod:`.fortran32`. A 64-bit process cannot load a 32-bit
library and therefore `inter-process communication <ipc_>`_ is used to interact with
a 32-bit library from a 64-bit process.

:class:`~.fortran64.Fortran64` is the 64-bit client and :class:`~.fortran32.Fortran32`
is the 32-bit server for `inter-process communication <ipc_>`_.

.. _ipc: https://en.wikipedia.org/wiki/Inter-process_communication
"""

from __future__ import annotations

import os
from typing import Sequence

from msl.loadlib import Client64


class Fortran64(Client64):
    def __init__(self) -> None:
        """Communicates with the 32-bit FORTRAN :ref:`fortran_lib32 <fortran-lib>` library.

        This class demonstrates how to communicate with a 32-bit FORTRAN library if an
        instance of this class is created within a 64-bit Python interpreter.
        """
        # specify the name of the corresponding 32-bit server module, fortran32, which hosts
        # the 32-bit FORTRAN library -- fortran_lib32.
        super().__init__(module32="fortran32", append_sys_path=os.path.dirname(__file__))

    def sum_8bit(self, a: int, b: int) -> int:
        """Send a request to add two 8-bit signed integers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.sum_8bit` method.

        :param a: First 8-bit signed integer.
        :param b: Second 8-bit signed integer.
        :return: The sum of `a` and `b`.
        """
        return self.request32("sum_8bit", a, b)

    def sum_16bit(self, a: int, b: int) -> int:
        """Send a request to add two 16-bit signed integers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.sum_16bit` method.

        :param a: First 16-bit signed integer.
        :param b: Second 16-bit signed integer.
        :return: The sum of `a` and `b`.
        """
        return self.request32("sum_16bit", a, b)

    def sum_32bit(self, a: int, b: int) -> int:
        """Send a request to add two 32-bit signed integers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.sum_32bit` method.

        :param a: First 32-bit signed integer.
        :param b: Second 32-bit signed integer.
        :return: The sum of `a` and `b`.
        """
        return self.request32("sum_32bit", a, b)

    def sum_64bit(self, a: int, b: int) -> int:
        """Send a request to add two 64-bit signed integers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.sum_64bit` method.

        :param a: First 64-bit signed integer.
        :param b: Second 64-bit signed integer.
        :return: The sum of `a` and `b`.
        """
        return self.request32("sum_64bit", a, b)

    def multiply_float32(self, a: float, b: float) -> float:
        """Send a request to multiply two FORTRAN floating-point numbers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.multiply_float32` method.

        :param a: First floating-point number.
        :param b: Second floating-point number.
        :return: The product of `a` and `b`.
        """
        return self.request32("multiply_float32", a, b)

    def multiply_float64(self, a: float, b: float) -> float:
        """Send a request to multiply two FORTRAN double-precision numbers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.multiply_float64` method.

        :param a: First double-precision number.
        :param b: Second double-precision number.
        :return: The product of `a` and `b`.
        """
        return self.request32("multiply_float64", a, b)

    def is_positive(self, a: float) -> bool:
        """Returns whether the value of the input argument is > 0.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.is_positive` method.

        :param a: Double-precision number.
        :return: Whether the value of `a` is > 0.
        """
        return self.request32("is_positive", a)

    def add_or_subtract(self, a: int, b: int, do_addition: bool) -> int:
        """Add or subtract two integers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.add_or_subtract` method.

        :param a: First integer.
        :param b: Second integer.
        :param do_addition: Whether to add or subtract the numbers.
        :return: `a+b` if `do_addition` is :data:`True` else `a-b`.
        """
        return self.request32("add_or_subtract", a, b, do_addition)

    def factorial(self, n: int) -> float:
        """Compute the n'th factorial.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.factorial` method.

        :param n: The integer to computer the factorial of. The maximum allowed value is 127.
        :return: The factorial of `n`.
        """
        return self.request32("factorial", n)

    def standard_deviation(self, data: Sequence[float]) -> float:
        """Compute the standard deviation.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.standard_deviation` method.

        :param data: The values to compute the standard deviation of.
        :return: The standard deviation of `data`.
        """
        return self.request32("standard_deviation", data)

    def besselJ0(self, x: float) -> float:
        """Compute the Bessel function of the first kind of order 0 of x.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.besselJ0` method.

        :param x: The value to compute ``BESSEL_J0`` of.
        :return: The value of ``BESSEL_J0(x)``.
        """
        return self.request32("besselJ0", x)

    def reverse_string(self, original: str) -> str:
        """Reverse a string.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.reverse_string` method.

        :param original: The original string.
        :return: The string reversed.
        """
        return self.request32("reverse_string", original)

    def add_1d_arrays(self, a1: Sequence[float], a2: Sequence[float]) -> list[float]:
        """Perform an element-wise addition of two 1D double-precision arrays.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.add_1d_arrays` method.

        :param a1: First array.
        :param a2: Second array.
        :return: The element-wise addition of `a1` + `a2`.
        """
        return self.request32("add_1d_arrays", a1, a2)

    def matrix_multiply(self, a1: Sequence[Sequence[float]], a2: Sequence[Sequence[float]]) -> list[list[float]]:
        """
        Multiply two matrices.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.matrix_multiply` method.

        :param a1: First matrix.
        :param a2: Second matrix.
        :return: The product of `a1` * `a2`.
        """
        return self.request32("matrix_multiply", a1, a2)
