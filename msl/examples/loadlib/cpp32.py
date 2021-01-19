"""
A wrapper around a 32-bit C++ library, :ref:`cpp_lib32 <cpp-lib>`.

Example of a server that loads a 32-bit shared library, :ref:`cpp_lib <cpp-lib>`,
in a 32-bit Python interpreter to host the library. The corresponding :mod:`~.cpp64` module
can be executed by a 64-bit Python interpreter and the :class:`~.cpp64.Cpp64` class can send
a request to the :class:`~.cpp32.Cpp32` class which calls the 32-bit library to execute the
request and then return the response from the library.
"""
import os
import math
import ctypes

from msl.loadlib import Server32


class Cpp32(Server32):

    def __init__(self, host, port, **kwargs):
        """A wrapper around the 32-bit C++ library, :ref:`cpp_lib32 <cpp-lib>`.

        This class demonstrates how to send/receive various data types to/from a
        32-bit C++ library via :mod:`ctypes`.

        Parameters
        ----------
        host : :class:`str`
            The IP address of the server.
        port : :class:`int`
            The port to open on the server.

        Note
        ----
        Any class that is a subclass of :class:`~msl.loadlib.server32.Server32` **MUST**
        provide two arguments in its constructor: `host` and `port` (in that order)
        and `**kwargs`. Otherwise the ``server32`` executable, see
        :class:`~msl.loadlib.start_server32`, cannot create an instance of the
        :class:`~msl.loadlib.server32.Server32` subclass.
        """
        # By not specifying the extension of the library file the server will open
        # the appropriate file based on the operating system.
        super(Cpp32, self).__init__(os.path.join(os.path.dirname(__file__), 'cpp_lib32'),
                                    'cdll', host, port)

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
        a : :class:`int`
            The first integer.
        b : :class:`int`
            The second integer.

        Returns
        -------
        :class:`int`
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
        a : :class:`float`
            The first floating-point number.
        b : :class:`float`
            The second floating-point number.

        Returns
        -------
        :class:`float`
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
        a : :class:`float`
            The first double-precision number.
        b : :class:`float`
            The second double-precision number.
        do_addition : :class:`bool`
            Whether to **add** the numbers.

        Returns
        -------
        :class:`float`
            Either `a` + `b` if `do_addition` is :data:`True` else `a` - `b`.
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
        a : :class:`float`
            The scalar value.
        xin : :class:`list` of :class:`float`
            The array to modify.

        Returns
        -------
        :class:`list` of :class:`float`
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
        original : :class:`str`
            The original string.

        Returns
        -------
        :class:`str`
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
        original : :class:`str`
            The original string.

        Returns
        -------
        :class:`str`
            The string reversed.
        """
        n = len(original)
        self.lib.reverse_string_v2.restype = ctypes.c_char_p
        rev = self.lib.reverse_string_v2(ctypes.c_char_p(original.encode()),
                                         ctypes.c_int32(n))
        return ctypes.string_at(rev, n).decode()

    def distance_4_points(self, points):
        """Calculates the total distance connecting 4 :class:`~.Point`\'s.

        The corresponding C++ code is

        .. code-block:: cpp

            double distance_4_points(FourPoints p) {
                double d = distance(p.points[0], p.points[3]);
                for (int i = 1; i < 4; i++) {
                    d += distance(p.points[i], p.points[i-1]);
                }
                return d;
            }

        See the corresponding 64-bit :meth:`~.cpp64.Cpp64.distance_4_points` method.

        Parameters
        ----------
        points : :class:`.FourPoints`
            The points to use to calculate the total distance.

        Returns
        -------
        :class:`float`
            The total distance connecting the 4 :class:`~.Point`\'s.
        """
        self.lib.distance_4_points.restype = ctypes.c_double
        return self.lib.distance_4_points(points)

    def circumference(self, radius, n):
        """Estimates the circumference of a circle.

        This method calls the ``distance_n_points`` function in :ref:`cpp_lib32 <cpp-lib>`.

        See the corresponding 64-bit :meth:`~.cpp64.Cpp64.circumference` method.

        The corresponding C++ code uses the :class:`.NPoints` struct as the input
        parameter to sum the distance between adjacent points on the circle.

        .. code-block:: cpp

            double distance_n_points(NPoints p) {
                if (p.n < 2) {
                    return 0.0;
                }
                double d = distance(p.points[0], p.points[p.n-1]);
                for (int i = 1; i < p.n; i++) {
                    d += distance(p.points[i], p.points[i-1]);
                }
                return d;
            }

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
        theta = 0.0
        delta = (2.0*math.pi)/float(n) if n != 0 else 0

        pts = NPoints()
        pts.n = n
        pts.points = (Point * n)()
        for i in range(n):
            pts.points[i] = Point(radius*math.cos(theta), radius*math.sin(theta))
            theta += delta

        self.lib.distance_n_points.restype = ctypes.c_double
        return self.lib.distance_n_points(pts)


class Point(ctypes.Structure):
    """C++ struct that is a fixed size in memory.

    This object can be :mod:`pickle`\'d.

    .. code-block:: cpp

       struct Point {
           double x;
           double y;
       };
    """
    _fields_ = [
        ('x', ctypes.c_double),
        ('y', ctypes.c_double),
    ]


class FourPoints(ctypes.Structure):

    _fields_ = [
        ('points', (Point * 4)),
    ]

    def __init__(self, point1, point2, point3, point4):
        """C++ struct that is a fixed size in memory.

        This object can be :mod:`pickle`\'d.

        .. code-block:: cpp

           struct FourPoints {
               Point points[4];
           };

        Parameters
        ----------
        point1 : :class:`tuple` of :class:`int`
            The first point as an (x, y) ordered pair.
        point2 : :class:`tuple` of :class:`int`
            The second point as an (x, y) ordered pair.
        point3 : :class:`tuple` of :class:`int`
            The third point as an (x, y) ordered pair.
        point4 : :class:`tuple` of :class:`int`
            The fourth point as an (x, y) ordered pair.
        """
        super(FourPoints, self).__init__()
        self.points = (Point * 4)(point1, point2, point3, point4)


class NPoints(ctypes.Structure):
    """C++ struct that is **not** a fixed size in memory.

    This object cannot be :mod:`pickle`\'d because it contains a pointer.
    A 32-bit process and a 64-bit process cannot share a pointer.

    .. code-block:: cpp

       struct NPoints {
           int n;
           Point *points;
       };
    """
    _fields_ = [
        ('n', ctypes.c_int),
        ('points', ctypes.POINTER(Point)),
    ]
