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
        Client64.__init__(self, module32='fortran32', append_sys_path=os.path.dirname(__file__))

    def sum_8bit(self, a, b):
        """Send a request to add two 8-bit signed integers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.sum_8bit` method.

        Parameters
        ----------
        a : :obj:`int`
            The first 8-bit signed integer.
        b : :obj:`int`
            The second 8-bit signed integer.

        Returns
        -------
        :obj:`int`
            The sum of `a` and `b`.
        """
        return self.request32('sum_8bit', a, b)

    def sum_16bit(self, a, b):
        """Send a request to add two 16-bit signed integers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.sum_16bit` method.

        Parameters
        ----------
        a : :obj:`int`
            The first 16-bit signed integer.
        b : :obj:`int`
            The second 16-bit signed integer.

        Returns
        -------
        :obj:`int`
            The sum of `a` and `b`.
        """
        return self.request32('sum_16bit', a, b)

    def sum_32bit(self, a, b):
        """Send a request to add two 32-bit signed integers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.sum_32bit` method.

        Parameters
        ----------
        a : :obj:`int`
            The first 32-bit signed integer.
        b : :obj:`int`
            The second 32-bit signed integer.

        Returns
        -------
        :obj:`int`
            The sum of `a` and `b`.
        """
        return self.request32('sum_32bit', a, b)

    def sum_64bit(self, a, b):
        """Send a request to add two 64-bit signed integers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.sum_64bit` method.

        Parameters
        ----------
        a : :obj:`int`
            The first 64-bit signed integer.
        b : :obj:`int`
            The second 64-bit signed integer.

        Returns
        -------
        :obj:`int`
            The sum of `a` and `b`.
        """
        return self.request32('sum_64bit', a, b)

    def multiply_float32(self, a, b):
        """Send a request to multiply two FORTRAN floating-point numbers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.multiply_float32` method.

        Parameters
        ----------
        a : :obj:`float`
            The first floating-point number.
        b : :obj:`float`
            The second floating-point number.

        Returns
        -------
        :obj:`float`
            The product of `a` and `b`.
        """
        return self.request32('multiply_float32', a, b)

    def multiply_float64(self, a, b):
        """Send a request to multiply two FORTRAN double-precision numbers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.multiply_float64` method.

        Parameters
        ----------
        a : :obj:`float`
            The first double-precision number.
        b : :obj:`float`
            The second double-precision number.

        Returns
        -------
        :obj:`float`
            The product of `a` and `b`.
        """
        return self.request32('multiply_float64', a, b)

    def is_positive(self, a):
        """Returns whether the value of the input argument is > 0.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.is_positive` method.

        Parameters
        ----------
        a : :obj:`float`
            A double-precision number.

        Returns
        -------
        :obj:`bool`
            Whether the value of `a` is > 0.
        """
        return self.request32('is_positive', a)

    def add_or_subtract(self, a, b, do_addition):
        """Add or subtract two integers.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.add_or_subtract` method.

        Parameters
        ----------
        a : :obj:`int`
            The first integer.
        b : :obj:`int`
            The second integer.
        do_addition : :obj:`bool`
            Whether to **add** the numbers.

        Returns
        -------
        :obj:`int`
            Either `a` + `b` if `do_addition` is :obj:`True` else `a` - `b`.
        """
        return self.request32('add_or_subtract', a, b, do_addition)

    def factorial(self, n):
        """Compute the n'th factorial.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.factorial` method.

        Parameters
        ----------
        n : :obj:`int`
            The integer to computer the factorial of. The maximum allowed value is 127.

        Returns
        -------
        :obj:`float`
            The factorial of `n`.
        """
        return self.request32('factorial', n)

    def standard_deviation(self, data):
        """Compute the standard deviation.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.standard_deviation` method.

        Parameters
        ----------
        data : :obj:`list` of :obj:`float`
            The data to compute the standard deviation of.

        Returns
        -------
        :obj:`float`
            The standard deviation of `data`.
        """
        return self.request32('standard_deviation', data)

    def besselJ0(self, x):
        """Compute the Bessel function of the first kind of order 0 of x.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.besselJ0` method.

        Parameters
        ----------
        x : :obj:`float`
            The value to compute ``BESSEL_J0`` of.

        Returns
        -------
        :obj:`float`
            The value of ``BESSEL_J0(x)``.
        """
        return self.request32('besselJ0', x)

    def reverse_string(self, original):
        """Reverse a string.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.reverse_string` method.

        Parameters
        ----------
        original : :obj:`str`
            The original string.

        Returns
        -------
        :obj:`str`
            The string reversed.
        """
        return self.request32('reverse_string', original)

    def add_1D_arrays(self, a1, a2):
        """Perform an element-wise addition of two 1D double-precision arrays.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.add_1D_arrays` method.

        Parameters
        ----------
        a1 : :obj:`list` of :obj:`float`
            The first array.
        a2 : :obj:`list` of :obj:`float`
            The second array.

        Returns
        -------
        :obj:`list` of :obj:`float`
            The element-wise addition of `a1` + `a2`.
        """
        return self.request32('add_1D_arrays', a1, a2)

    def matrix_multiply(self, a1, a2):
        """
        Multiply two matrices.

        See the corresponding 32-bit :meth:`~.fortran32.Fortran32.matrix_multiply` method.

        Parameters
        ----------
        a1 : :obj:`list` of :obj:`list` of :obj:`float`
            The first matrix.
        a2 : :obj:`list` of :obj:`list` of :obj:`float`
            The second matrix.

        Returns
        -------
        :obj:`list` of :obj:`list` of :obj:`float`
            The result of `a1` * `a2`.
        """
        return self.request32('matrix_multiply', a1, a2)


if __name__ == '__main__':
    import re
    import inspect

    def display(value):
        caller = re.findall(r'f.\w+', inspect.stack()[1][4][0])
        print('{} {} {}'.format(caller[0], type(value), value))

    f = Fortran64()
    print(f.lib32_path)
    display(f.sum_8bit(-50, 110))
    display(f.sum_16bit(2**15-1, -1))
    display(f.sum_32bit(123456788, 1))
    display(f.sum_64bit(-2**63, 1))
    display(f.multiply_float32(1e30, 2e3))
    display(f.multiply_float64(1e30, 2e3))
    display(f.is_positive(1e-100))
    display(f.is_positive(-1e-100))
    display(f.add_or_subtract(1000, 2000, True))
    display(f.add_or_subtract(1000, 2000, False))
    display(f.factorial(127))
    display(f.standard_deviation([float(val) for val in range(1,10)]))
    display(f.besselJ0(8))
    display(f.reverse_string('hello world!'))
    display(f.add_1D_arrays([float(val) for val in range(1, 10)], [3.0*val for val in range(1, 10)]))
    display(f.matrix_multiply([[1, 2, 3], [4, 5, 6]], [[1, 2], [3, 4], [5, 6]]))
