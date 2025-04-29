"""Communicates with the [cpp_lib][cpp-lib] library via the [Cpp32][] class that is running on a server."""

from __future__ import annotations

import os
from typing import Sequence

from msl.examples.loadlib import FourPoints
from msl.loadlib import Client64


class Cpp64(Client64):
    """Communicates with a 32-bit C++ library."""

    def __init__(self) -> None:
        """Communicates with a 32-bit C++ library via the server running [Cpp32][].

        This class demonstrates how to communicate with a 32-bit C++ library if an
        instance of this class is created within a 64-bit Python interpreter.
        """
        # specify the name of the corresponding 32-bit server module, cpp32, which hosts
        # the 32-bit C++ library -- cpp_lib32.
        super().__init__(module32="cpp32", append_sys_path=os.path.dirname(__file__))

    def add(self, a: int, b: int) -> int:
        """Add two integers.

        See the corresponding [Cpp32.add][msl.examples.loadlib.cpp32.Cpp32.add] method.

        Args:
            a: First integer.
            b: Second integer.

        Returns:
            The sum, `a + b`.
        """
        return self.request32("add", a, b)

    def subtract(self, a: float, b: float) -> float:
        """Subtract two floating-point numbers *('float' refers to the C++ data type)*.

        See the corresponding [Cpp32.subtract][msl.examples.loadlib.cpp32.Cpp32.subtract] method.

        Args:
            a: First floating-point number.
            b: Second floating-point number.

        Returns:
            The difference, `a - b`.
        """
        return self.request32("subtract", a, b)

    def add_or_subtract(self, a: float, b: float, do_addition: bool) -> float:
        """Add or subtract two floating-point numbers *('double' refers to the C++ data type)*.

        See the corresponding [Cpp32.add_or_subtract][msl.examples.loadlib.cpp32.Cpp32.add_or_subtract] method.

        Args:
            a: First double-precision number.
            b: Second double-precision number.
            do_addition: Whether to add or subtract the numbers.

        Returns:
            `a + b` if `do_addition` is `True` else `a - b`.
        """
        return self.request32("add_or_subtract", a, b, do_addition)

    def scalar_multiply(self, a: float, xin: Sequence[float]) -> list[float]:
        """Multiply each element in an array by a number.

        See the corresponding [Cpp32.scalar_multiply][msl.examples.loadlib.cpp32.Cpp32.scalar_multiply] method.

        Args:
            a: Scalar value.
            xin: Array to modify.

        Returns:
            A new array with each element in `xin` multiplied by `a`.
        """
        return self.request32("scalar_multiply", a, xin)

    def reverse_string_v1(self, original: str) -> str:
        """Reverse a string (version 1).

        In this method Python allocates the memory for the reversed string
        and passes the string to C++.

        See the corresponding [Cpp32.reverse_string_v1][msl.examples.loadlib.cpp32.Cpp32.reverse_string_v1] method.

        Args:
            original: The original string.

        Returns:
            The string reversed.
        """
        return self.request32("reverse_string_v1", original)

    def reverse_string_v2(self, original: str) -> str:
        """Reverse a string (version 2).

        In this method C++ allocates the memory for the reversed string and passes
        the string to Python.

        See the corresponding [Cpp32.reverse_string_v2][msl.examples.loadlib.cpp32.Cpp32.reverse_string_v2] method.

        Args:
            original: The original string.

        Returns:
            The string reversed.
        """
        return self.request32("reverse_string_v2", original)

    def distance_4_points(self, points: FourPoints) -> float:
        """Calculates the total distance connecting 4 [Point][msl.examples.loadlib.cpp32.Point]s.

        See the corresponding [Cpp32.distance_4_points][msl.examples.loadlib.cpp32.Cpp32.distance_4_points] method.

        Args:
            points: The points to use to calculate the total distance.
                Since `points` is a struct that is a fixed size we can pass the
                [ctypes.Structure][]{:target="_blank"} object directly from 64-bit Python to
                the 32-bit Python. The [ctypes][]{:target="_blank"} module on the 32-bit server
                can load the [pickle][]{:target="_blank"}d [ctypes.Structure][]{:target="_blank"}.

        Returns:
            The total distance connecting the 4 points.
        """
        if not isinstance(points, FourPoints):
            msg = f"Must pass in a FourPoints object. Got {type(points)}"
            raise TypeError(msg)
        return self.request32("distance_4_points", points)

    def circumference(self, radius: float, n: int) -> float:
        """Estimates the circumference of a circle.

        This method calls the `distance_n_points` function in [cpp_lib][cpp-lib].

        See the corresponding [Cpp32.circumference][msl.examples.loadlib.cpp32.Cpp32.circumference] method.

        Args:
            radius: The radius of the circle.
            n: The number of points to use to estimate the circumference.

        Returns:
            The estimated circumference of the circle.
        """
        return self.request32("circumference", radius, n)
