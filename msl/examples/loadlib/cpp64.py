"""
Communicates with :ref:`cpp_lib32 <cpp-lib>` via the :class:`~.cpp32.Cpp32` class.

Example of a module that can be executed within a 64-bit Python interpreter which can
communicate with a 32-bit library, :ref:`cpp_lib32 <cpp-lib>`, that is hosted
by a 32-bit Python server, :mod:`.cpp32`. A 64-bit process cannot load a
32-bit library and therefore `inter-process communication <ipc_>`_ is used to
interact with a 32-bit library from a 64-bit process.

:class:`~.cpp64.Cpp64` is the 64-bit client and :class:`~.cpp32.Cpp32`
is the 32-bit server for `inter-process communication <ipc_>`_.

.. _ipc: https://en.wikipedia.org/wiki/Inter-process_communication
"""
from __future__ import annotations

import os
from typing import Sequence

from msl.examples.loadlib import FourPoints
from msl.loadlib import Client64


class Cpp64(Client64):

    def __init__(self) -> None:
        """Communicates with a 32-bit C++ library, :ref:`cpp_lib32 <cpp-lib>`.

        This class demonstrates how to communicate with a 32-bit C++ library if an
        instance of this class is created within a 64-bit Python interpreter.
        """
        # specify the name of the corresponding 32-bit server module, cpp32, which hosts
        # the 32-bit C++ library -- cpp_lib32.
        super().__init__(module32='cpp32', append_sys_path=os.path.dirname(__file__))

    def add(self, a: int, b: int) -> int:
        """Add two integers.

        See the corresponding 32-bit :meth:`~.cpp32.Cpp32.add` method.

        :param a: First integer.
        :param b: Second integer.
        :return: The sum of `a` and `b`.
        """
        return self.request32('add', a, b)

    def subtract(self, a: float, b: float) -> float:
        """Subtract two floating-point numbers *('float' refers to the C++ data type)*.

        See the corresponding 32-bit :meth:`~.cpp32.Cpp32.subtract` method.

        :param a: First floating-point number.
        :param b: Second floating-point number.
        :return: The difference between `a` and `b`.
        """
        return self.request32('subtract', a, b)

    def add_or_subtract(self, a: float, b: float, do_addition: bool) -> float:
        """Add or subtract two floating-point numbers *('double' refers to the C++ data type)*.

        See the corresponding 32-bit :meth:`~.cpp32.Cpp32.add_or_subtract` method.

        :param a: First double-precision number.
        :param b: Second double-precision number.
        :param do_addition: Whether to add or subtract the numbers.
        :return: `a+b` if `do_addition` is :data:`True` else `a-b`.
        """
        return self.request32('add_or_subtract', a, b, do_addition)

    def scalar_multiply(self, a: float, xin: Sequence[float]) -> list[float]:
        """Multiply each element in an array by a number.

        See the corresponding 32-bit :meth:`~.cpp32.Cpp32.scalar_multiply` method.

        :param a: Scalar value.
        :param xin: Array to modify.
        :return: A new array with each element in `xin` multiplied by `a`.
        """
        return self.request32('scalar_multiply', a, xin)

    def reverse_string_v1(self, original: str) -> str:
        """Reverse a string (version 1).

        In this method Python allocates the memory for the reversed string
        and passes the string to C++.

        See the corresponding 32-bit :meth:`~.cpp32.Cpp32.reverse_string_v1` method.

        :param original: The original string.
        :return: The string reversed.
        """
        return self.request32('reverse_string_v1', original)

    def reverse_string_v2(self, original: str) -> str:
        """Reverse a string (version 2).

        In this method C++ allocates the memory for the reversed string and passes
        the string to Python.

        See the corresponding 32-bit :meth:`~.cpp32.Cpp32.reverse_string_v2` method.

        :param original: The original string.
        :return: The string reversed.
        """
        return self.request32('reverse_string_v2', original)

    def distance_4_points(self, points: FourPoints) -> float:
        """Calculates the total distance connecting 4 :class:`~msl.examples.loadlib.cpp32.Point`\'s.

        See the corresponding 32-bit :meth:`~.cpp32.Cpp32.distance_4_points` method.

        :param points: The points to use to calculate the total distance.
            Since `points` is a struct that is a fixed size we can pass the
            :class:`ctypes.Structure` object directly from 64-bit Python to
            the 32-bit Python. The :mod:`ctypes` module on the 32-bit server
            can load the :mod:`pickle`\'d :class:`ctypes.Structure`.
        :return: The total distance connecting the 4 points.
        """
        if not isinstance(points, FourPoints):
            raise TypeError(f'Must pass in a FourPoints object. Got {type(points)}')
        return self.request32('distance_4_points', points)

    def circumference(self, radius: float, n: int) -> float:
        """Estimates the circumference of a circle.

        This method calls the ``distance_n_points`` function in :ref:`cpp_lib32 <cpp-lib>`.

        See the corresponding 32-bit :meth:`~.cpp32.Cpp32.circumference` method.

        :param radius: The radius of the circle.
        :param n: The number of points to use to estimate the circumference.
        :return: The estimated circumference of the circle.
        """
        return self.request32('circumference', radius, n)
