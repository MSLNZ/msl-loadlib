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
import os

from msl.loadlib import Client64
from msl.examples.loadlib.cpp32 import FourPoints


class Cpp64(Client64):
    """Communicates with a 32-bit C++ library, :ref:`cpp_lib32 <cpp-lib>`.

    This class demonstrates how to communicate with a 32-bit C++ library if an 
    instance of this class is created within a 64-bit Python interpreter.
    """
    def __init__(self):
        # specify the name of the corresponding 32-bit server module, cpp32, which hosts
        # the 32-bit C++ library -- cpp_lib32.
        super(Cpp64, self).__init__(module32='cpp32', append_sys_path=os.path.dirname(__file__))

    def add(self, a, b):
        """Add two integers.

        See the corresponding 32-bit :meth:`~.cpp32.Cpp32.add` method.

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
        return self.request32('add', a, b)

    def subtract(self, a, b):
        """Subtract two floating-point numbers *('float' refers to the C++ data type)*.

        See the corresponding 32-bit :meth:`~.cpp32.Cpp32.subtract` method.

        Parameters
        ----------
        a : :class:`float`
            The first floating-point number.
        b : :class:`float`
            The second floating-point number.

        Returns
        -------
        :class:`float`
            The difference between `a` and `b`.
        """
        return self.request32('subtract', a, b)

    def add_or_subtract(self, a, b, do_addition):
        """Add or subtract two floating-point numbers *('double' refers to the C++ data type)*.

        See the corresponding 32-bit :meth:`~.cpp32.Cpp32.add_or_subtract` method.

        Parameters
        ----------
        a : :class:`float`
            The first floating-point number.
        b : :class:`float`
            The second floating-point number.
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

        See the corresponding 32-bit :meth:`~.cpp32.Cpp32.scalar_multiply` method.

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

    def reverse_string_v1(self, original):
        """Reverse a string (version 1).

        In this method Python allocates the memory for the reversed string
        and passes the string to C++.

        See the corresponding 32-bit :meth:`~.cpp32.Cpp32.reverse_string_v1` method.

        Parameters
        ----------
        original : :class:`str`
            The original string.

        Returns
        -------
        :class:`str`
            The string reversed.
        """
        return self.request32('reverse_string_v1', original)

    def reverse_string_v2(self, original):
        """Reverse a string (version 2).

        In this method C++ allocates the memory for the reversed string and passes
        the string to Python.

        See the corresponding 32-bit :meth:`~.cpp32.Cpp32.reverse_string_v2` method.

        Parameters
        ----------
        original : :class:`str`
            The original string.

        Returns
        -------
        :class:`str`
            The string reversed.
        """
        return self.request32('reverse_string_v2', original)

    def distance_4_points(self, points):
        """Calculates the total distance connecting 4 :class:`~msl.examples.loadlib.cpp32.Point`\'s.

        See the corresponding 32-bit :meth:`~.cpp32.Cpp32.distance_4_points` method.

        .. attention::
           This method does not work with if :class:`Cpp64` is running in Python 2.
           You would have to create the :class:`.FourPoints` object in the 32-bit
           version of :meth:`~.cpp32.Cpp32.distance_4_points` because there are issues
           using the :mod:`pickle` module between different major version numbers of
           Python for :mod:`ctypes` objects.

        Parameters
        ----------
        points : :class:`.FourPoints`
            Since `points` is a struct that is a fixed size we can pass the
            :class:`ctypes.Structure` object directly from 64-bit Python to
            the 32-bit Python. The :mod:`ctypes` module on the 32-bit server
            can load the :mod:`pickle`\'d :class:`ctypes.Structure`.

        Returns
        -------
        :class:`float`
            The total distance connecting the 4 :class:`~.Point`\'s.
        """
        if not isinstance(points, FourPoints):
            raise TypeError('Must pass in a FourPoints object. Got {}'.format(type(points)))
        return self.request32('distance_4_points', points)

    def circumference(self, radius, n):
        """Estimates the circumference of a circle.

        This method calls the ``distance_n_points`` function in :ref:`cpp_lib32 <cpp-lib>`.

        See the corresponding 32-bit :meth:`~.cpp32.Cpp32.circumference` method.

        Parameters
        ----------
        radius : :class:`float`
            The radius of the circle.
        n : :class:`int`
            The number of points to use to estimate the circumference.

        Returns
        -------
        :class:`float`
            The estimated circumference of the circle.
        """
        return self.request32('circumference', radius, n)
