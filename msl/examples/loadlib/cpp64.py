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


class Cpp64(Client64):
    """Communicates with a 32-bit C++ library, :ref:`cpp_lib32 <cpp-lib>`.

    This class demonstrates how to communicate with a 32-bit C++ library if an 
    instance of this class is created within a 64-bit Python interpreter.
    """
    def __init__(self):
        # specify the name of the corresponding 32-bit server module, cpp32, which hosts
        # the 32-bit C++ library -- cpp_lib32.
        Client64.__init__(self, module32='cpp32', append_sys_path=os.path.dirname(__file__))

    def add(self, a, b):
        """Add two integers.

        See the corresponding 32-bit :meth:`~.cpp32.Cpp32.add` method.

        Parameters
        ----------
        a : :obj:`int`
            The first integer.
        b : :obj:`int`
            The second integer.

        Returns
        -------
        :obj:`int`
            The sum of `a` and `b`.
        """
        return self.request32('add', a, b)

    def subtract(self, a, b):
        """Subtract two floating-point numbers *('float' refers to the C++ data type)*.

        See the corresponding 32-bit :meth:`~.cpp32.Cpp32.subtract` method.

        Parameters
        ----------
        a : :obj:`float`
            The first floating-point number.
        b : :obj:`float`
            The second floating-point number.

        Returns
        -------
        :obj:`float`
            The difference between `a` and `b`.
        """
        return self.request32('subtract', a, b)

    def add_or_subtract(self, a, b, do_addition):
        """Add or subtract two floating-point numbers *('double' refers to the C++ data type)*.

        See the corresponding 32-bit :meth:`~.cpp32.Cpp32.add_or_subtract` method.

        Parameters
        ----------
        a : :obj:`float`
            The first floating-point number.
        b : :obj:`float`
            The second floating-point number.
        do_addition : :obj:`bool`
            Whether to **add** the numbers.

        Returns
        -------
        :obj:`float`
            Either `a` + `b` if `do_addition` is :obj:`True` else `a` - `b`.
        """
        return self.request32('add_or_subtract', a, b, do_addition)

    def scalar_multiply(self, a, xin):
        """Multiply each element in an array by a number.

        See the corresponding 32-bit :meth:`~.cpp32.Cpp32.scalar_multiply` method.

        Parameters
        ----------
        a : :obj:`float`
            The scalar value.
        xin : :obj:`list` of :obj:`float`
            The array to modify.

        Returns
        -------
        :obj:`list` of :obj:`float`
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
        original : :obj:`str`
            The original string.

        Returns
        -------
        :obj:`str`
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
        original : :obj:`str`
            The original string.

        Returns
        -------
        :obj:`str`
            The string reversed.
        """
        return self.request32('reverse_string_v2', original)


if __name__ == '__main__':
    import re
    import inspect

    def display(value):
        caller = re.findall(r'cpp.\w+', inspect.stack()[1][4][0])
        print('{} {} {}'.format(caller[0], type(value), value))

    x, y, = 3, 7
    cpp = Cpp64()
    print(cpp.lib32_path)
    display(cpp.add(x, y))
    display(cpp.subtract(x, y))
    display(cpp.add_or_subtract(x, y, True))
    display(cpp.add_or_subtract(x, y, False))
    display(cpp.scalar_multiply(2., [float(val) for val in range(10)]))
    display(cpp.reverse_string_v1('hello world!'))
    display(cpp.reverse_string_v2('uncertainty'))
