"""Wrapper around a 32-bit FORTRAN library.

Example of a server that loads a 32-bit library, [fortran_lib32][fortran-lib],
in a 32-bit Python interpreter to host the library. The corresponding [Fortran64][] class
is created in a 64-bit Python interpreter and the [Fortran64][] class sends requests
to the [Fortran32][] class which calls the 32-bit library to execute the request and
then returns the response from the library.
"""

from __future__ import annotations

import ctypes
import os
from typing import Sequence

from msl.loadlib import Server32


class Fortran32(Server32):
    """Wrapper around a 32-bit FORTRAN library."""

    def __init__(self, host: str, port: int) -> None:
        """A wrapper around a 32-bit FORTRAN library, [fortran_lib32][fortran-lib].

        This class demonstrates how to pass various data types to/from a
        32-bit FORTRAN library via [ctypes][]{:target="_blank"}.

        Args:
            host: The IP address (or hostname) to use for the server.
            port: The port to open for the server.
        """
        # By not specifying the extension of the library file the server will open
        # the appropriate file based on the operating system.
        path = os.path.join(os.path.dirname(__file__), "fortran_lib32")
        super().__init__(path, "cdll", host, port)

    def sum_8bit(self, a: int, b: int) -> int:
        """Add two 8-bit signed integers.

        Python only has one [int][]{:target="_blank"} data type to represent integer values.
        This method converts the data types of `a` and `b` to be
        [c_int8][ctypes.c_int8]{:target="_blank"}.

        The corresponding FORTRAN code is

        ```fortran
        function sum_8bit(a, b) result(value)
            !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'sum_8bit' :: sum_8bit
            implicit none
            integer(1) :: a, b, value
            value = a + b
        end function sum_8bit
        ```

        See the corresponding [Fortran64.sum_8bit][msl.examples.loadlib.fortran64.Fortran64.sum_8bit] method.

        Args:
            a: First 8-bit signed integer.
            b: Second 8-bit signed integer.

        Returns:
            The sum, `a + b`.
        """
        # restype should be defined elsewhere, shown here for illustrative purposes
        self.lib.sum_8bit.restype = ctypes.c_int8

        ac = ctypes.c_int8(a)
        bc = ctypes.c_int8(b)
        return self.lib.sum_8bit(ctypes.byref(ac), ctypes.byref(bc))

    def sum_16bit(self, a: int, b: int) -> int:
        """Add two 16-bit signed integers.

        Python only has one [int][]{:target="_blank"} data type to represent integer values.
        This method converts the data types of `a` and `b` to be
        [c_int16][ctypes.c_int16]{:target="_blank"}.

        The corresponding FORTRAN code is

        ```fortran
        function sum_16bit(a, b) result(value)
            !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'sum_16bit' :: sum_16bit
            implicit none
            integer(2) :: a, b, value
            value = a + b
        end function sum_16bit
        ```

        See the corresponding [Fortran64.sum_16bit][msl.examples.loadlib.fortran64.Fortran64.sum_16bit] method.

        Args:
            a: First 16-bit signed integer.
            b: Second 16-bit signed integer.

        Returns:
            The sum, `a + b`.
        """
        # restype should be defined elsewhere, shown here for illustrative purposes
        self.lib.sum_16bit.restype = ctypes.c_int16

        ac = ctypes.c_int16(a)
        bc = ctypes.c_int16(b)
        return self.lib.sum_16bit(ctypes.byref(ac), ctypes.byref(bc))

    def sum_32bit(self, a: int, b: int) -> int:
        """Add two 32-bit signed integers.

        Python only has one [int][]{:target="_blank"} data type to represent integer values.
        This method converts the data types of `a` and `b` to be
        [c_int32][ctypes.c_int32]{:target="_blank"}.

        The corresponding FORTRAN code is

        ```fortran
        function sum_32bit(a, b) result(value)
            !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'sum_32bit' :: sum_32bit
            implicit none
            integer(4) :: a, b, value
            value = a + b
        end function sum_32bit
        ```

        See the corresponding [Fortran64.sum_32bit][msl.examples.loadlib.fortran64.Fortran64.sum_32bit] method.

        Args:
            a: First 32-bit signed integer.
            b: Second 32-bit signed integer.

        Returns:
            The sum, `a + b`.
        """
        # restype should be defined elsewhere, shown here for illustrative purposes
        self.lib.sum_32bit.restype = ctypes.c_int32

        ac = ctypes.c_int32(a)
        bc = ctypes.c_int32(b)
        return self.lib.sum_32bit(ctypes.byref(ac), ctypes.byref(bc))

    def sum_64bit(self, a: int, b: int) -> int:
        """Add two 64-bit signed integers.

        Python only has one [int][]{:target="_blank"} data type to represent integer values.
        This method converts the data types of `a` and `b` to be
        [c_int64][ctypes.c_int64]{:target="_blank"}.

        The corresponding FORTRAN code is

        ```fortran
        function sum_64bit(a, b) result(value)
            !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'sum_64bit' :: sum_64bit
            implicit none
            integer(8) :: a, b, value
            value = a + b
        end function sum_64bit
        ```

        See the corresponding [Fortran64.sum_64bit][msl.examples.loadlib.fortran64.Fortran64.sum_64bit] method.

        Args:
            a: First 64-bit signed integer.
            b: Second 64-bit signed integer.

        Returns:
            The sum, `a + b`.
        """
        # restype should be defined elsewhere, shown here for illustrative purposes
        self.lib.sum_64bit.restype = ctypes.c_int64

        ac = ctypes.c_int64(a)
        bc = ctypes.c_int64(b)
        return self.lib.sum_64bit(ctypes.byref(ac), ctypes.byref(bc))

    def multiply_float32(self, a: float, b: float) -> float:
        """Multiply two FORTRAN floating-point numbers.

        The corresponding FORTRAN code is

        ```fortran
        function multiply_float32(a, b) result(value)
            !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'multiply_float32' :: multiply_float32
            implicit none
            real(4) :: a, b, value
            value = a * b
        end function multiply_float32
        ```

        See the corresponding [Fortran64.multiply_float32][msl.examples.loadlib.fortran64.Fortran64.multiply_float32]
        method.

        Args:
            a: First floating-point number.
            b: Second floating-point number.

        Returns:
            The product, `a * b`.
        """
        # restype should be defined elsewhere, shown here for illustrative purposes
        self.lib.multiply_float32.restype = ctypes.c_float

        ac = ctypes.c_float(a)
        bc = ctypes.c_float(b)
        return self.lib.multiply_float32(ctypes.byref(ac), ctypes.byref(bc))

    def multiply_float64(self, a: float, b: float) -> float:
        """Multiply two FORTRAN double-precision numbers.

        The corresponding FORTRAN code is

        ```fortran
        function multiply_float64(a, b) result(value)
            !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'multiply_float64' :: multiply_float64
            implicit none
            real(8) :: a, b, value
            value = a * b
        end function multiply_float64
        ```

        See the corresponding [Fortran64.multiply_float64][msl.examples.loadlib.fortran64.Fortran64.multiply_float64]
        method.

        Args:
            a: First double-precision number.
            b: Second double-precision number.

        Returns:
            The product, `a * b`.
        """
        # restype should be defined elsewhere, shown here for illustrative purposes
        self.lib.multiply_float64.restype = ctypes.c_double

        ac = ctypes.c_double(a)
        bc = ctypes.c_double(b)
        return self.lib.multiply_float64(ctypes.byref(ac), ctypes.byref(bc))

    def is_positive(self, a: float) -> bool:
        """Returns whether the value of the input argument is > 0.

        The corresponding FORTRAN code is

        ```fortran
        function is_positive(a) result(value)
            !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'is_positive' :: is_positive
            implicit none
            logical :: value
            real(8) :: a
            value = a > 0.d0
        end function is_positive
        ```

        See the corresponding [Fortran64.is_positive][msl.examples.loadlib.fortran64.Fortran64.is_positive] method.

        Args:
            a: Double-precision number.


        Returns:
            Whether the value of `a` is &gt; 0.
        """
        # restype should be defined elsewhere, shown here for illustrative purposes
        self.lib.is_positive.restype = ctypes.c_bool

        ac = ctypes.c_double(a)
        return self.lib.is_positive(ctypes.byref(ac))

    def add_or_subtract(self, a: int, b: int, do_addition: bool) -> int:
        """Add or subtract two integers.

        The corresponding FORTRAN code is

        ```fortran
        function add_or_subtract(a, b, do_addition) result(value)
            !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'add_or_subtract' :: add_or_subtract
            implicit none
            logical :: do_addition
            integer(4) :: a, b, value
            if (do_addition) then
                value = a + b
            else
                value = a - b
            endif
        end function add_or_subtract
        ```

        See the corresponding [Fortran64.add_or_subtract][msl.examples.loadlib.fortran64.Fortran64.add_or_subtract] method.

        Args:
            a: First integer.
            b: Second integer.
            do_addition: Whether to add or subtract the numbers.

        Return:
            `a + b` if `do_addition` is `True` else `a - b`.
        """
        # restype should be defined elsewhere, shown here for illustrative purposes
        self.lib.add_or_subtract.restype = ctypes.c_int32

        ac = ctypes.c_int32(a)
        bc = ctypes.c_int32(b)
        logical = ctypes.c_bool(do_addition)
        return self.lib.add_or_subtract(ctypes.byref(ac), ctypes.byref(bc), ctypes.byref(logical))

    def factorial(self, n: int) -> float:
        """Compute the n'th factorial.

        The corresponding FORTRAN code is

        ```fortran
        function factorial(n) result(value)
            !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'factorial' :: factorial
            implicit none
            integer(1) :: n
            integer(4) :: i
            double precision value
            if (n < 0) then
                value = 0.d0
                print *, "Cannot compute the factorial of a negative number", n
            else
                value = 1.d0
                do i = 2, n
                    value = value * i
                enddo
            endif
        end function factorial
        ```

        See the corresponding [Fortran64.factorial][msl.examples.loadlib.fortran64.Fortran64.factorial] method.

        Args:
            n: The integer to computer the factorial of. The maximum allowed value is 127.

        Returns:
            The factorial of `n`.
        """
        # restype should be defined elsewhere, shown here for illustrative purposes
        self.lib.factorial.restype = ctypes.c_double

        ac = ctypes.c_int8(n)
        return self.lib.factorial(ctypes.byref(ac))

    def standard_deviation(self, data: Sequence[float]) -> float:
        """Compute the standard deviation.

        The corresponding FORTRAN code is

        ```fortran
        function standard_deviation(a, n) result(var)
            !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'standard_deviation' :: standard_deviation
            integer :: n ! the length of the array
            double precision :: var, a(n)
            var = SUM(a)/SIZE(a) ! SUM is a built-in fortran function
            var = SQRT(SUM((a-var)**2)/(SIZE(a)-1.0))
        end function standard_deviation
        ```

        See the corresponding [Fortran64.standard_deviation][msl.examples.loadlib.fortran64.Fortran64.standard_deviation]
        method.

        Args:
            data: The values to compute the standard deviation of.

        Returns:
            The standard deviation of `data`.
        """
        # restype should be defined elsewhere, shown here for illustrative purposes
        self.lib.standard_deviation.restype = ctypes.c_double

        n = len(data)
        nc = ctypes.c_int32(n)
        data_c = (ctypes.c_double * n)(*data)
        return self.lib.standard_deviation(ctypes.byref(data_c), ctypes.byref(nc))

    def besselJ0(self, x: float) -> float:
        """Compute the Bessel function of the first kind of order 0 of x.

        The corresponding FORTRAN code is

        ```fortran
        function besselj0(x) result(val)
            !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'besselj0' :: besselj0
            double precision :: x, val
            val = BESSEL_J0(x)
        end function besselJ0
        ```

        See the corresponding [Fortran64.besselJ0][msl.examples.loadlib.fortran64.Fortran64.besselJ0] method.

        Args:
            x: The value to compute `BESSEL_J0` of.

        Returns:
            The value of `BESSEL_J0(x)`.
        """
        # restype should be defined elsewhere, shown here for illustrative purposes
        self.lib.besselj0.restype = ctypes.c_double

        xc = ctypes.c_double(x)
        return self.lib.besselj0(ctypes.byref(xc))

    def reverse_string(self, original: str) -> str:
        """Reverse a string.

        The corresponding FORTRAN code is

        ```fortran
        subroutine reverse_string(original, n, reversed)
            !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'reverse_string' :: reverse_string
            !DEC$ ATTRIBUTES REFERENCE :: original, reversed
            implicit none
            integer :: i, n
            character(len=n) :: original, reversed
            do i = 1, n
                reversed(i:i) = original(n-i+1:n-i+1)
            end do
        end subroutine reverse_string
        ```

        See the corresponding [Fortran64.reverse_string][msl.examples.loadlib.fortran64.Fortran64.reverse_string] method.

        Args:
            original: The original string.

        Returns:
            The string reversed.
        """
        # restype should be defined elsewhere, shown here for illustrative purposes
        self.lib.reverse_string.restype = None

        n = len(original)
        nc = ctypes.c_int32(n)
        rev = ctypes.create_string_buffer(n)
        self.lib.reverse_string(ctypes.c_char_p(original.encode()), ctypes.byref(nc), rev)
        return rev.raw.decode()

    def add_1d_arrays(self, a1: Sequence[float], a2: Sequence[float]) -> list[float]:
        """Perform an element-wise addition of two 1D double-precision arrays.

        The corresponding FORTRAN code is

        ```fortran
        subroutine add_1d_arrays(a, in1, in2, n)
            !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'add_1d_arrays' :: add_1d_arrays
            implicit none
            integer(4) :: n ! the length of the input arrays
            double precision :: in1(n), in2(n) ! the arrays to add (element-wise)
            double precision :: a(n) ! the array that will contain the element-wise sum
            a(:) = in1(:) + in2(:)
        end subroutine add_1d_arrays
        ```

        See the corresponding [Fortran64.add_1d_arrays][msl.examples.loadlib.fortran64.Fortran64.add_1d_arrays] method.

        Args:
            a1: First array.
            a2: Second array.

        Returns:
            The element-wise addition of `a1 + a2`.
        """
        # restype should be defined elsewhere, shown here for illustrative purposes
        self.lib.add_1d_arrays.restype = None

        n = len(a1)
        nc = ctypes.c_int32(n)
        out = (ctypes.c_double * n)()
        self.lib.add_1d_arrays(out, (ctypes.c_double * n)(*a1), (ctypes.c_double * n)(*a2), ctypes.byref(nc))
        return [val for val in out]

    def matrix_multiply(self, a1: Sequence[Sequence[float]], a2: Sequence[Sequence[float]]) -> list[list[float]]:
        """Multiply two matrices.

        The corresponding FORTRAN code is

        ```fortran
        subroutine matrix_multiply(a, a1, r1, c1, a2, r2, c2)
            !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'matrix_multiply' :: matrix_multiply
            implicit none
            integer(4) :: r1, c1, r2, c2 ! the dimensions of the input arrays
            double precision :: a1(r1,c1), a2(r2,c2) ! the arrays to multiply
            double precision :: a(r1,c2) ! resultant array
            a = MATMUL(a1, a2)
        end subroutine matrix_multiply
        ```

        !!! note
            FORTRAN stores multidimensional arrays in [column-major order][order]{:target="_blank"},
            as opposed to [row-major order][order]{:target="_blank"} like C (Python) arrays. Therefore,
            the input matrices need to be transposed before sending the matrices to FORTRAN
            and also the result needs to be transposed.

            [order]: https://en.wikipedia.org/wiki/Row-_and_column-major_order

        See the corresponding [Fortran64.matrix_multiply][msl.examples.loadlib.fortran64.Fortran64.matrix_multiply]
        method.

        Args:
            a1: First matrix.
            a2: Second matrix.

        Returns:
            The product, `a1 @ a2`.
        """
        # restype should be defined elsewhere, shown here for illustrative purposes
        self.lib.matrix_multiply.restype = None

        n_rows1 = ctypes.c_int32(len(a1))
        n_cols1 = ctypes.c_int32(len(a1[0]))

        n_rows2 = ctypes.c_int32(len(a2))
        n_cols2 = ctypes.c_int32(len(a2[0]))

        if n_cols1.value != n_rows2.value:
            msg = (
                f"Cannot multiply a {n_rows1.value}x{n_cols1.value} matrix "
                f"with a {n_rows2.value}x{n_cols2.value} matrix"
            )
            raise ValueError(msg)

        m1 = ((ctypes.c_double * n_rows1.value) * n_cols1.value)()
        for r in range(n_rows1.value):
            for c in range(n_cols1.value):
                m1[c][r] = a1[r][c]

        m2 = ((ctypes.c_double * n_rows2.value) * n_cols2.value)()
        for r in range(n_rows2.value):
            for c in range(n_cols2.value):
                m2[c][r] = a2[r][c]

        out = ((ctypes.c_double * n_rows1.value) * n_cols2.value)()

        self.lib.matrix_multiply(
            out, m1, ctypes.byref(n_rows1), ctypes.byref(n_cols1), m2, ctypes.byref(n_rows2), ctypes.byref(n_cols2)
        )

        return [[out[c][r] for c in range(n_cols2.value)] for r in range(n_rows1.value)]
