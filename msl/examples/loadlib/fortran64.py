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
import os

from msl.loadlib import Client64


class Fortran64(Client64):
    """Communicates with the 32-bit FORTRAN :ref:`fortran_lib32 <fortran-lib>` library.

    This class demonstrates how to communicate with a 32-bit FORTRAN library if an 
    instance of this class is created within a 64-bit Python interpreter.
    """
    def __init__(self):
        # specify the name of the corresponding 32-bit server module, fortran32, which hosts
        # the 32-bit FORTRAN library -- fortran_lib32.
        super(Fortran64, self).__init__(module32='fortran32', append_sys_path=os.path.dirname(__file__))

    def sum_8bit(self, a, b):
        """Send a request to add two 8-bit signed integers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.sum_8bit` method.

        Parameters
        ----------
        a : :class:`int`
            The first 8-bit signed integer.
        b : :class:`int`
            The second 8-bit signed integer.

        Returns
        -------
        :class:`int`
            The sum of `a` and `b`.
        """
        return self.request32('sum_8bit', a, b)

    def sum_16bit(self, a, b):
        """Send a request to add two 16-bit signed integers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.sum_16bit` method.

        Parameters
        ----------
        a : :class:`int`
            The first 16-bit signed integer.
        b : :class:`int`
            The second 16-bit signed integer.

        Returns
        -------
        :class:`int`
            The sum of `a` and `b`.
        """
        return self.request32('sum_16bit', a, b)

    def sum_32bit(self, a, b):
        """Send a request to add two 32-bit signed integers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.sum_32bit` method.

        Parameters
        ----------
        a : :class:`int`
            The first 32-bit signed integer.
        b : :class:`int`
            The second 32-bit signed integer.

        Returns
        -------
        :class:`int`
            The sum of `a` and `b`.
        """
        return self.request32('sum_32bit', a, b)

    def sum_64bit(self, a, b):
        """Send a request to add two 64-bit signed integers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.sum_64bit` method.

        Parameters
        ----------
        a : :class:`int`
            The first 64-bit signed integer.
        b : :class:`int`
            The second 64-bit signed integer.

        Returns
        -------
        :class:`int`
            The sum of `a` and `b`.
        """
        return self.request32('sum_64bit', a, b)

    def multiply_float32(self, a, b):
        """Send a request to multiply two FORTRAN floating-point numbers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.multiply_float32` method.

        Parameters
        ----------
        a : :class:`float`
            The first floating-point number.
        b : :class:`float`
            The second floating-point number.

        Returns
        -------
        :class:`float`
            The product of `a` and `b`.
        """
        return self.request32('multiply_float32', a, b)

    def multiply_float64(self, a, b):
        """Send a request to multiply two FORTRAN double-precision numbers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.multiply_float64` method.

        Parameters
        ----------
        a : :class:`float`
            The first double-precision number.
        b : :class:`float`
            The second double-precision number.

        Returns
        -------
        :class:`float`
            The product of `a` and `b`.
        """
        return self.request32('multiply_float64', a, b)

    def is_positive(self, a):
        """Returns whether the value of the input argument is > 0.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.is_positive` method.

        Parameters
        ----------
        a : :class:`float`
            A double-precision number.

        Returns
        -------
        :class:`bool`
            Whether the value of `a` is > 0.
        """
        return self.request32('is_positive', a)

    def add_or_subtract(self, a, b, do_addition):
        """Add or subtract two integers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.add_or_subtract` method.

        Parameters
        ----------
        a : :class:`int`
            The first integer.
        b : :class:`int`
            The second integer.
        do_addition : :class:`bool`
            Whether to **add** the numbers.

        Returns
        -------
        :class:`int`
            Either `a` + `b` if `do_addition` is :data:`True` else `a` - `b`.
        """
        return self.request32('add_or_subtract', a, b, do_addition)

    def factorial(self, n):
        """Compute the n'th factorial.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.factorial` method.

        Parameters
        ----------
        n : :class:`int`
            The integer to computer the factorial of. The maximum allowed value is 127.

        Returns
        -------
        :class:`float`
            The factorial of `n`.
        """
        return self.request32('factorial', n)

    def standard_deviation(self, data):
        """Compute the standard deviation.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.standard_deviation` method.

        Parameters
        ----------
        data : :class:`list` of :class:`float`
            The data to compute the standard deviation of.

        Returns
        -------
        :class:`float`
            The standard deviation of `data`.
        """
        return self.request32('standard_deviation', data)

    def besselJ0(self, x):
        """Compute the Bessel function of the first kind of order 0 of x.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.besselJ0` method.

        Parameters
        ----------
        x : :class:`float`
            The value to compute ``BESSEL_J0`` of.

        Returns
        -------
        :class:`float`
            The value of ``BESSEL_J0(x)``.
        """
        return self.request32('besselJ0', x)

    def reverse_string(self, original):
        """Reverse a string.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.reverse_string` method.

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

    def add_1D_arrays(self, a1, a2):
        """Perform an element-wise addition of two 1D double-precision arrays.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.add_1D_arrays` method.

        Parameters
        ----------
        a1 : :class:`list` of :class:`float`
            The first array.
        a2 : :class:`list` of :class:`float`
            The second array.

        Returns
        -------
        :class:`list` of :class:`float`
            The element-wise addition of `a1` + `a2`.
        """
        return self.request32('add_1D_arrays', a1, a2)

    def matrix_multiply(self, a1, a2):
        """
        Multiply two matrices.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.matrix_multiply` method.

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
        return self.request32('matrix_multiply', a1, a2)
