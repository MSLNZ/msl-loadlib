"""Wrapper around a 32-bit C++ library.

Example of a server that loads a 32-bit library, [cpp_lib][cpp-lib],
in a 32-bit Python interpreter to host the library. The corresponding [Cpp64][] class
is created in a 64-bit Python interpreter and the [Cpp64][] class sends requests
to the [Cpp32][] class which calls the 32-bit library to execute the request and
then returns the response from the library.
"""

from __future__ import annotations

import ctypes
import math
from pathlib import Path
from typing import TYPE_CHECKING

from msl.loadlib import Server32

if TYPE_CHECKING:
    from collections.abc import Sequence
    from ctypes import Array


class Cpp32(Server32):
    """Wrapper around a 32-bit C++ library."""

    def __init__(self, host: str, port: int) -> None:
        """Wrapper around a 32-bit C++ library.

        This class demonstrates how to send/receive various data types to/from a
        32-bit C++ library via [ctypes][]{:target="_blank"}.

        Args:
            host: The IP address (or hostname) to use for the server.
            port: The port to open for the server.
        """
        # By not specifying the extension of the library file the server will open
        # the appropriate file based on the operating system.
        path = Path(__file__).parent / "cpp_lib32"
        super().__init__(path, "cdll", host, port)

    def add(self, a: int, b: int) -> int:
        """Add two integers.

        The corresponding C++ code is

        ```cpp
        int add(int a, int b) {
            return a + b;
        }
        ```

        See the corresponding [Cpp64.add][msl.examples.loadlib.cpp64.Cpp64.add] method.

        Args:
            a: First integer.
            b: Second integer.

        Returns:
            The sum, `a + b`.
        """
        # restype and argtypes should be defined elsewhere, shown here for illustrative purposes
        self.lib.add.restype = ctypes.c_int32
        self.lib.add.argtypes = [ctypes.c_int32, ctypes.c_int32]
        result: int = self.lib.add(a, b)
        return result

    def subtract(self, a: float, b: float) -> float:
        """Subtract two floating-point numbers *('float' refers to the C++ data type)*.

        The corresponding C++ code is

        ```cpp
        float subtract(float a, float b) {
            return a - b;
        }
        ```

        See the corresponding [Cpp64.subtract][msl.examples.loadlib.cpp64.Cpp64.subtract] method.

        Args:
            a: First floating-point number.
            b: Second floating-point number.

        Returns:
            The difference, `a - b`.
        """
        # restype and argtypes should be defined elsewhere, shown here for illustrative purposes
        self.lib.subtract.restype = ctypes.c_float
        self.lib.subtract.argtypes = [ctypes.c_float, ctypes.c_float]
        result: float = self.lib.subtract(a, b)
        return result

    def add_or_subtract(self, a: float, b: float, *, do_addition: bool) -> float:
        """Add or subtract two double-precision numbers *('double' refers to the C++ data type)*.

        The corresponding C++ code is

        ```cpp
        double add_or_subtract(double a, double b, bool do_addition) {
            if (do_addition) {
                return a + b;
            } else {
                return a - b;
            }
        }
        ```

        See the corresponding [Cpp64.add_or_subtract][msl.examples.loadlib.cpp64.Cpp64.add_or_subtract] method.

        Args:
            a: First double-precision number.
            b: Second double-precision number.
            do_addition: Whether to add or subtract the numbers.

        Returns:
            `a + b` if `do_addition` is `True` else `a - b`.
        """
        # restype and argtypes should be defined elsewhere, shown here for illustrative purposes
        self.lib.add_or_subtract.restype = ctypes.c_double
        self.lib.add_or_subtract.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_bool]
        result: float = self.lib.add_or_subtract(a, b, do_addition)
        return result

    def scalar_multiply(self, a: float, xin: Sequence[float]) -> list[float]:
        """Multiply each element in an array by a number.

        The corresponding C++ code is

        ```cpp
        void scalar_multiply(double a, double* xin, int n, double* xout) {
            for (int i = 0; i < n; i++) {
                xout[i] = a * xin[i];
            }
        }
        ```

        See the corresponding [Cpp64.scalar_multiply][msl.examples.loadlib.cpp64.Cpp64.scalar_multiply] method.

        Args:
            a: Scalar value.
            xin: Array to modify.

        Returns:
            A new array with each element in `xin` multiplied by `a`.
        """
        # restype and argtypes should be defined elsewhere, shown here for illustrative purposes
        self.lib.scalar_multiply.restype = None
        self.lib.scalar_multiply.argtypes = [
            ctypes.c_double,
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_int32,
            ctypes.POINTER(ctypes.c_double),
        ]

        n = len(xin)
        c_xin = (ctypes.c_double * n)(*xin)  # convert input array to ctypes
        c_xout = (ctypes.c_double * n)()  # allocate memory for output array
        self.lib.scalar_multiply(a, c_xin, n, c_xout)
        return list(c_xout)

    def reverse_string_v1(self, original: str) -> str:
        """Reverse a string (version 1).

        In this method Python allocates the memory for the reversed string and
        passes the string to C++.

        The corresponding C++ code is

        ```cpp
        void reverse_string_v1(const char* original, int n, char* reversed) {
            for (int i = 0; i < n; i++) {
                reversed[i] = original[n-i-1];
            }
        }
        ```

        See the corresponding [Cpp64.reverse_string_v1][msl.examples.loadlib.cpp64.Cpp64.reverse_string_v1] method.

        Args:
            original: The original string.

        Returns:
            The string reversed.
        """
        # restype and argtypes should be defined elsewhere, shown here for illustrative purposes
        self.lib.reverse_string_v1.restype = None
        self.lib.reverse_string_v1.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_char_p]

        n = len(original)
        rev = ctypes.create_string_buffer(n)
        self.lib.reverse_string_v1(original.encode(), n, rev)
        return rev.raw.decode()

    def reverse_string_v2(self, original: str) -> str:
        """Reverse a string (version 2).

        In this method C++ allocates the memory for the reversed string and passes
        the string to Python.

        The corresponding C++ code is

        ```cpp
        char* reverse_string_v2(char* original, int n) {
            char* reversed = new char[n];
            for (int i = 0; i < n; i++) {
                reversed[i] = original[n - i - 1];
            }
            return reversed;
        }
        ```

        See the corresponding [Cpp64.reverse_string_v2][msl.examples.loadlib.cpp64.Cpp64.reverse_string_v2] method.

        Args:
            original: The original string.

        Returns:
            The string reversed.
        """
        # restype and argtypes should be defined elsewhere, shown here for illustrative purposes
        self.lib.reverse_string_v2.restype = ctypes.c_char_p
        self.lib.reverse_string_v2.argtypes = [ctypes.c_char_p, ctypes.c_int32]

        n = len(original)
        rev = self.lib.reverse_string_v2(original.encode(), n)
        return ctypes.string_at(rev, n).decode()

    def distance_4_points(self, four_points: FourPoints) -> float:
        """Calculates the total distance connecting 4 [Point][msl.examples.loadlib.cpp32.Point]s.

        The corresponding C++ code is

        ```cpp
        double distance_4_points(FourPoints p) {
            double d = distance(p.points[0], p.points[3]);
            for (int i = 1; i < 4; i++) {
                d += distance(p.points[i], p.points[i-1]);
            }
            return d;
        }
        ```

        See the corresponding [Cpp64.distance_4_points][msl.examples.loadlib.cpp64.Cpp64.distance_4_points] method.

        Args:
            four_points: The points to use to calculate the total distance.

        Returns:
            The total distance connecting the 4 points.
        """
        # restype should be defined elsewhere, shown here for illustrative purposes
        self.lib.distance_4_points.restype = ctypes.c_double
        result: float = self.lib.distance_4_points(four_points)
        return result

    def circumference(self, radius: float, n: int) -> float:
        """Estimates the circumference of a circle.

        This method calls the `distance_n_points` function in [cpp_lib][cpp-lib].

        The corresponding C++ code uses the [NPoints][msl.examples.loadlib.cpp32.NPoints]
        struct as the input parameter to sum the distance between adjacent points on the circle.

        ```cpp
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
        ```

        See the corresponding [Cpp64.circumference][msl.examples.loadlib.cpp64.Cpp64.circumference] method.

        Args:
            radius: The radius of the circle.
            n: The number of points to use to estimate the circumference.

        Returns:
            The estimated circumference of the circle.
        """
        # restype and argtypes should be defined elsewhere, shown here for illustrative purposes
        self.lib.distance_n_points.restype = ctypes.c_double
        self.lib.distance_n_points.argtypes = [NPoints]

        theta = 0.0
        delta = (2.0 * math.pi) / float(n) if n != 0 else 0

        pts = NPoints()
        pts.n = n
        pts.points = (Point * n)()
        for i in range(n):
            pts.points[i] = Point(radius * math.cos(theta), radius * math.sin(theta))
            theta += delta
        result: float = self.lib.distance_n_points(pts)
        return result


class Point(ctypes.Structure):
    """C++ struct that is a fixed size in memory.

    This object can be [pickle][]{:target="_blank"}d.

    ```cpp
    struct Point {
        double x;
        double y;
    };
    ```
    """

    _fields_ = (  # pyright: ignore[reportUnannotatedClassAttribute]
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
    )


class FourPoints(ctypes.Structure):
    """C++ struct that is a fixed size in memory."""

    _fields_ = (  # pyright: ignore[reportUnannotatedClassAttribute]
        ("points", (Point * 4)),
    )

    def __init__(self, point1: Point, point2: Point, point3: Point, point4: Point) -> None:
        """C++ struct that is a fixed size in memory.

        This object can be [pickle][]{:target="_blank"}d.

        ```cpp
        struct FourPoints {
            Point points[4];
        };
        ```

        Args:
            point1: The first point.
            point2: The second point.
            point3: The third point.
            point4: The fourth point.
        """
        super().__init__()
        self.points: Array[Point] = (Point * 4)(point1, point2, point3, point4)


class NPoints(ctypes.Structure):
    """C++ struct that is **not** a fixed size in memory.

    This object cannot be [pickle][]{:target="_blank"}d because it contains a pointer.
    A 32-bit process and a 64-bit process cannot share a pointer.

    ```cpp
    struct NPoints {
        int n;
        Point *points;
    };
    ```
    """

    _fields_ = (  # pyright: ignore[reportUnannotatedClassAttribute]
        ("n", ctypes.c_int),
        ("points", ctypes.POINTER(Point)),
    )
