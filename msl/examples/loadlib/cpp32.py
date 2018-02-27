"""
A wrapper around a 32-bit C++ library, :ref:`cpp_lib32 <cpp-lib>`.

Example of a server that loads a 32-bit shared library, :ref:`cpp_lib <cpp-lib>`,
in a 32-bit Python interpreter to host the library. The corresponding :mod:`~.cpp64` module
can be executed by a 64-bit Python interpreter and the :class:`~.cpp64.Cpp64` class can send
a request to the :class:`~.cpp32.Cpp32` class which calls the 32-bit library to execute the
request and then return the response from the library.
"""
import os
import ctypes

from msl.loadlib import Server32


class Cpp32(Server32):
    """A wrapper around the 32-bit C++ library, :ref:`cpp_lib32 <cpp-lib>`.

    This class demonstrates how to send/receive various data types to/from a
    32-bit C++ library via :py:mod:`ctypes`.

    Parameters
    ----------
    host : :obj:`str`
        The IP address of the server.
    port : :obj:`int`
        The port to open on the server.
    quiet : :obj:`bool`
        Whether to hide :obj:`sys.stdout` messages from the server.

    Note
    ----
    Any class that is a subclass of :class:`~msl.loadlib.server32.Server32` **MUST**
    provide three arguments in its constructor: `host`, `port` and `quiet`
    (in that order) and `**kwargs`. Otherwise the ``server32`` executable, see
    :class:`~msl.loadlib.start_server32`, cannot create an instance of the
    :class:`~msl.loadlib.server32.Server32` subclass.
    """
    def __init__(self, host, port, quiet, **kwargs):
        # By not specifying the extension of the library file the server will open
        # the appropriate file based on the operating system.
        Server32.__init__(self, os.path.join(os.path.dirname(__file__), 'cpp_lib32'),
                          'cdll', host, port, quiet)

    def add(self, a, b):
        """Add two integers.

        The corresponding C++ code is

        .. code-block:: cpp

            int add(int a, int b) {
                return a + b;
            }

        See the corresponding 64-bit :meth:`~.cpp64.Cpp64.add` method.

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
        return self.lib.add(ctypes.c_int32(a), ctypes.c_int32(b))

    def subtract(self, a, b):
        """Subtract two floating-point numbers *('float' refers to the C++ data type)*.

        The corresponding C++ code is

        .. code-block:: cpp

            float subtract(float a, float b) {
                return a - b;
            }

        See the corresponding 64-bit :meth:`~.cpp64.Cpp64.subtract` method.

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
        self.lib.subtract.restype = ctypes.c_float
        return self.lib.subtract(ctypes.c_float(a), ctypes.c_float(b))

    def add_or_subtract(self, a, b, do_addition):
        """Add or subtract two double-precision numbers *('double' refers to the C++ data type)*.

        The corresponding C++ code is

        .. code-block:: cpp

            double add_or_subtract(double a, double b, bool do_addition) {
                if (do_addition) {
                    return a + b;
                } else {
                    return a - b;
                }
            }

        See the corresponding 64-bit :meth:`~.cpp64.Cpp64.add_or_subtract` method.

        Parameters
        ----------
        a : :obj:`float`
            The first double-precision number.
        b : :obj:`float`
            The second double-precision number.
        do_addition : :obj:`bool`
            Whether to **add** the numbers.

        Returns
        -------
        :obj:`float`
            Either `a` + `b` if `do_addition` is :obj:`True` else `a` - `b`.
        """
        self.lib.add_or_subtract.restype = ctypes.c_double
        return self.lib.add_or_subtract(ctypes.c_double(a), ctypes.c_double(b), do_addition)

    def scalar_multiply(self, a, xin):
        """Multiply each element in an array by a number.

        The corresponding C++ code is

        .. code-block:: cpp

            void scalar_multiply(double a, double* xin, int n, double* xout) {
                for (int i = 0; i < n; i++) {
                    xout[i] = a * xin[i];
                }
            }

        See the corresponding 64-bit :meth:`~.cpp64.Cpp64.scalar_multiply` method.

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
        n = len(xin)
        xout = (ctypes.c_double * n)()  # allocate memory

        self.lib.scalar_multiply.restype = None

        self.lib.scalar_multiply(ctypes.c_double(float(a)),
                                 (ctypes.c_double * n)(*xin),
                                 ctypes.c_int32(n),
                                 ctypes.byref(xout))
        return [value for value in xout]

    def reverse_string_v1(self, original):
        """Reverse a string (version 1).

        In this method Python allocates the memory for the reversed string and
        passes the string to C++.

        The corresponding C++ code is

        .. code-block:: cpp

            void reverse_string_v1(const char* original, int n, char* reversed) {
                for (int i = 0; i < n; i++) {
                    reversed[i] = original[n-i-1];
                }
            }

        See the corresponding 64-bit :meth:`~.cpp64.Cpp64.reverse_string_v1` method.

        Parameters
        ----------
        original : :obj:`str`
            The original string.

        Returns
        -------
        :obj:`str`
            The string reversed.
        """
        n = len(original)

        # use create_string_buffer since 'rev' gets modified in the library
        rev = ctypes.create_string_buffer(n)

        self.lib.reverse_string_v1.restype = None
        self.lib.reverse_string_v1(ctypes.c_char_p(original.encode()),
                                   ctypes.c_int32(n),
                                   rev)
        return rev.raw.decode()

    def reverse_string_v2(self, original):
        """Reverse a string (version 2).

        In this method C++ allocates the memory for the reversed string and passes
        the string to Python.

        The corresponding C++ code is

        .. code-block:: cpp

            char* reverse_string_v2(char* original, int n) {
                char* reversed = new char[n];
                for (int i = 0; i < n; i++) {
                    reversed[i] = original[n - i - 1];
                }
                return reversed;
            }

        See the corresponding 64-bit :meth:`~.cpp64.Cpp64.reverse_string_v2` method.

        Parameters
        ----------
        original : :obj:`str`
            The original string.

        Returns
        -------
        :obj:`str`
            The string reversed.
        """
        n = len(original)
        self.lib.reverse_string_v2.restype = ctypes.c_char_p
        rev = self.lib.reverse_string_v2(ctypes.c_char_p(original.encode()),
                                         ctypes.c_int32(n))
        return ctypes.string_at(rev, n).decode()
