"""
A wrapper around a 32-bit FORTRAN library, :ref:`fortran_lib32 <fortran-lib>`.

Example of a server that loads a 32-bit FORTRAN library, :ref:`fortran_lib32 <fortran-lib>`,
in a 32-bit Python interpreter to host the library. The corresponding :mod:`~.fortran64`
module can be executed by a 64-bit Python interpreter and the :class:`~.fortran64.Fortran64`
class can send a request to the :class:`~.fortran32.Fortran32` class which calls the 32-bit
library to execute the request and then return the response from the library.
"""
import os
import ctypes

from msl.loadlib import Server32


class Fortran32(Server32):

    def __init__(self, host, port, **kwargs):
        """A wrapper around a 32-bit FORTRAN library, :ref:`fortran_lib32 <fortran-lib>`.

        This class demonstrates how to send/receive various data types to/from a
        32-bit FORTRAN library via :py:mod:`ctypes`. For a summary of the FORTRAN
        data types see `here <https://earth.uni-muenster.de/~joergs/doc/f90/unix-um/dfum_034.html>`_.

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
        super(Fortran32, self).__init__(os.path.join(os.path.dirname(__file__), 'fortran_lib32'),
                                        'cdll', host, port)

    def sum_8bit(self, a, b):
        """Add two 8-bit signed integers. 
        
        Python only has one :class:`int` data type to represent integer values.
        The :meth:`~.fortran32.Fortran32.sum_8bit` method converts the data types 
        of `a` and `b` to be :class:`ctypes.c_int8`.

        The corresponding FORTRAN code is

        .. code-block:: fortran

            function sum_8bit(a, b) result(value)
                !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'sum_8bit' :: sum_8bit
                implicit none
                integer(1) :: a, b, value
                value = a + b
            end function sum_8bit

        See the corresponding 64-bit :meth:`~.fortran64.Fortran64.sum_8bit` method.

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
        ac = ctypes.c_int8(a)
        bc = ctypes.c_int8(b)
        self.lib.sum_8bit.restype = ctypes.c_int8
        return self.lib.sum_8bit(ctypes.byref(ac), ctypes.byref(bc))

    def sum_16bit(self, a, b):
        """Add two 16-bit signed integers
        
        Python only has one :class:`int` data type to represent integer values.
        The :meth:`~.fortran32.Fortran32.sum_16bit` method converts the data 
        types of `a` and `b` to be :class:`ctypes.c_int16`.

        The corresponding FORTRAN code is

        .. code-block:: fortran

            function sum_16bit(a, b) result(value)
                !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'sum_16bit' :: sum_16bit
                implicit none
                integer(2) :: a, b, value
                value = a + b
            end function sum_16bit

        See the corresponding 64-bit :meth:`~.fortran64.Fortran64.sum_16bit` method.

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
        ac = ctypes.c_int16(a)
        bc = ctypes.c_int16(b)
        self.lib.sum_16bit.restype = ctypes.c_int16
        return self.lib.sum_16bit(ctypes.byref(ac), ctypes.byref(bc))

    def sum_32bit(self, a, b):
        """Add two 32-bit signed integers. 
        
        Python only has one :class:`int` data type to represent integer values.
        The :meth:`~.fortran32.Fortran32.sum_32bit` method converts the data types 
        of `a` and `b` to be :class:`ctypes.c_int32`.

        The corresponding FORTRAN code is

        .. code-block:: fortran

            function sum_32bit(a, b) result(value)
                !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'sum_32bit' :: sum_32bit
                implicit none
                integer(4) :: a, b, value
                value = a + b
            end function sum_32bit

        See the corresponding 64-bit :meth:`~.fortran64.Fortran64.sum_32bit` method.

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
        ac = ctypes.c_int32(a)
        bc = ctypes.c_int32(b)
        self.lib.sum_32bit.restype = ctypes.c_int32
        return self.lib.sum_32bit(ctypes.byref(ac), ctypes.byref(bc))

    def sum_64bit(self, a, b):
        """Add two 64-bit signed integers. 
        
        Python only has one :class:`int` data type to represent integer values.
        The :meth:`~.fortran32.Fortran32.sum_64bit` method converts the data types 
        of `a` and `b` to be :class:`ctypes.c_int64`.

        The corresponding FORTRAN code is

        .. code-block:: fortran

            function sum_64bit(a, b) result(value)
                !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'sum_64bit' :: sum_64bit
                implicit none
                integer(8) :: a, b, value
                value = a + b
            end function sum_64bit

        See the corresponding 64-bit :meth:`~.fortran64.Fortran64.sum_64bit` method.

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
        ac = ctypes.c_int64(a)
        bc = ctypes.c_int64(b)
        self.lib.sum_64bit.restype = ctypes.c_int64
        return self.lib.sum_64bit(ctypes.byref(ac), ctypes.byref(bc))

    def multiply_float32(self, a, b):
        """Multiply two FORTRAN floating-point numbers.

        The corresponding FORTRAN code is

        .. code-block:: fortran

            function multiply_float32(a, b) result(value)
                !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'multiply_float32' :: multiply_float32
                implicit none
                real(4) :: a, b, value
                value = a * b
            end function multiply_float32

        See the corresponding 64-bit :meth:`~.fortran64.Fortran64.multiply_float32` method.

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
        ac = ctypes.c_float(a)
        bc = ctypes.c_float(b)
        self.lib.multiply_float32.restype = ctypes.c_float
        return self.lib.multiply_float32(ctypes.byref(ac), ctypes.byref(bc))

    def multiply_float64(self, a, b):
        """Multiply two FORTRAN double-precision numbers.

        The corresponding FORTRAN code is

        .. code-block:: fortran

            function multiply_float64(a, b) result(value)
                !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'multiply_float64' :: multiply_float64
                implicit none
                real(8) :: a, b, value
                value = a * b
            end function multiply_float64

        See the corresponding 64-bit :meth:`~.fortran64.Fortran64.multiply_float64` method.

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
        ac = ctypes.c_double(a)
        bc = ctypes.c_double(b)
        self.lib.multiply_float64.restype = ctypes.c_double
        return self.lib.multiply_float64(ctypes.byref(ac), ctypes.byref(bc))

    def is_positive(self, a):
        """Returns whether the value of the input argument is > 0.

        The corresponding FORTRAN code is

        .. code-block:: fortran

            function is_positive(a) result(value)
                !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'is_positive' :: is_positive
                implicit none
                logical :: value
                real(8) :: a
                value = a > 0.d0
            end function is_positive

        See the corresponding 64-bit :meth:`~.fortran64.Fortran64.is_positive` method.

        Parameters
        ----------
        a : :class:`float`
            A double-precision number.

        Returns
        -------
        :class:`bool`
            Whether the value of `a` is > 0.
        """
        ac = ctypes.c_double(a)
        self.lib.is_positive.restype = ctypes.c_bool
        return self.lib.is_positive(ctypes.byref(ac))

    def add_or_subtract(self, a, b, do_addition):
        """Add or subtract two integers.

        The corresponding FORTRAN code is

        .. code-block:: fortran

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

        See the corresponding 64-bit :meth:`~.fortran64.Fortran64.add_or_subtract` method.

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
        ac = ctypes.c_int32(a)
        bc = ctypes.c_int32(b)
        logical = ctypes.c_bool(do_addition)
        self.lib.add_or_subtract.restype = ctypes.c_int32
        return self.lib.add_or_subtract(ctypes.byref(ac), ctypes.byref(bc), ctypes.byref(logical))

    def factorial(self, n):
        """Compute the n'th factorial.

        The corresponding FORTRAN code is

        .. code-block:: fortran

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

        See the corresponding 64-bit :meth:`~.fortran64.Fortran64.factorial` method.

        Parameters
        ----------
        n : :class:`int`
            The integer to computer the factorial of. The maximum allowed value is 127.

        Returns
        -------
        :class:`float`
            The factorial of `n`.
        """
        ac = ctypes.c_int8(n)
        self.lib.factorial.restype = ctypes.c_double
        return self.lib.factorial(ctypes.byref(ac))

    def standard_deviation(self, data):
        """Compute the standard deviation.

        The corresponding FORTRAN code is

        .. code-block:: fortran

            function standard_deviation(a, n) result(var)
                !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'standard_deviation' :: standard_deviation
                integer :: n ! the length of the array
                double precision :: var, a(n)
                var = SUM(a)/SIZE(a) ! SUM is a built-in fortran function
                var = SQRT(SUM((a-var)**2)/(SIZE(a)-1.0))
            end function standard_deviation

        See the corresponding 64-bit :meth:`~.fortran64.Fortran64.standard_deviation` method.

        Parameters
        ----------
        data : :class:`list` of :class:`float`
            The data to compute the standard deviation of.

        Returns
        -------
        :class:`float`
            The standard deviation of `data`.
        """
        n = len(data)
        nc = ctypes.c_int32(n)
        datac = (ctypes.c_double * n)(*data)
        self.lib.standard_deviation.restype = ctypes.c_double
        return self.lib.standard_deviation(ctypes.byref(datac), ctypes.byref(nc))

    def besselJ0(self, x):
        """Compute the Bessel function of the first kind of order 0 of x.

        The corresponding FORTRAN code is

        .. code-block:: fortran

            function besselj0(x) result(val)
                !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'besselj0' :: besselj0
                double precision :: x, val
                val = BESSEL_J0(x)
            end function besselJ0

        See the corresponding 64-bit :meth:`~.fortran64.Fortran64.besselJ0` method.

        Parameters
        ----------
        x : :class:`float`
            The value to compute ``BESSEL_J0`` of.

        Returns
        -------
        :class:`float`
            The value of ``BESSEL_J0(x)``.
        """
        xc = ctypes.c_double(x)
        self.lib.besselj0.restype = ctypes.c_double
        return self.lib.besselj0(ctypes.byref(xc))

    def reverse_string(self, original):
        """Reverse a string.

        The corresponding FORTRAN code is

        .. code-block:: fortran

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

        See the corresponding 64-bit :meth:`~.fortran64.Fortran64.reverse_string` method.

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
        nc = ctypes.c_int32(n)
        rev = ctypes.create_string_buffer(n)
        self.lib.reverse_string.restype = None
        self.lib.reverse_string(ctypes.c_char_p(original.encode()),
                                ctypes.byref(nc),
                                rev)
        return rev.raw.decode()

    def add_1D_arrays(self, a1, a2):
        """Perform an element-wise addition of two 1D double-precision arrays.

        The corresponding FORTRAN code is

        .. code-block:: fortran

            subroutine add_1d_arrays(a, in1, in2, n)
                !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'add_1d_arrays' :: add_1d_arrays
                implicit none
                integer(4) :: n ! the length of the input arrays
                double precision :: in1(n), in2(n) ! the arrays to add (element-wise)
                double precision :: a(n) ! the array that will contain the element-wise sum
                a(:) = in1(:) + in2(:)
            end subroutine add_1D_arrays

        See the corresponding 64-bit :meth:`~.fortran64.Fortran64.add_1D_arrays` method.

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
        n = len(a1)
        nc = ctypes.c_int32(n)
        out = (ctypes.c_double * n)()

        self.lib.add_1d_arrays.restype = None
        self.lib.add_1d_arrays(out,
                               (ctypes.c_double * n)(*a1),
                               (ctypes.c_double * n)(*a2),
                               ctypes.byref(nc))
        return [val for val in out]

    def matrix_multiply(self, a1, a2):
        """Multiply two matrices.

        The corresponding FORTRAN code is

        .. code-block:: fortran

            subroutine matrix_multiply(a, a1, r1, c1, a2, r2, c2)
                !DEC$ ATTRIBUTES DLLEXPORT, ALIAS:'matrix_multiply' :: matrix_multiply
                implicit none
                integer(4) :: r1, c1, r2, c2 ! the dimensions of the input arrays
                double precision :: a1(r1,c1), a2(r2,c2) ! the arrays to multiply
                double precision :: a(r1,c2) ! resultant array
                a = MATMUL(a1, a2)
            end subroutine matrix_multiply

        Note
        ----
        FORTRAN stores multi-dimensional arrays in `column-major order <order_>`_, as
        opposed to `row-major order <order_>`_ for C (Python) arrays. Therefore the
        input matrices need to be transposed before sending the matrices to FORTRAN
        and also the result needs to be transposed before returning the result.

        .. _order: https://en.wikipedia.org/wiki/Row-_and_column-major_order
        
        See the corresponding 64-bit :meth:`~.fortran64.Fortran64.matrix_multiply` method.

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
        nrows1 = ctypes.c_int32(len(a1))
        ncols1 = ctypes.c_int32(len(a1[0]))

        nrows2 = ctypes.c_int32(len(a2))
        ncols2 = ctypes.c_int32(len(a2[0]))

        if not ncols1.value == nrows2.value:
            msg = "Cannot multiply a {}x{} matrix with a {}x{} matrix"
            raise ValueError(msg.format(nrows1.value, ncols1.value, nrows2.value, ncols2.value))

        m1 = ((ctypes.c_double * nrows1.value) * ncols1.value)()
        for r in range(nrows1.value):
            for c in range(ncols1.value):
                m1[c][r] = a1[r][c]

        m2 = ((ctypes.c_double * nrows2.value) * ncols2.value)()
        for r in range(nrows2.value):
            for c in range(ncols2.value):
                m2[c][r] = a2[r][c]

        out = ((ctypes.c_double * nrows1.value) * ncols2.value)()

        self.lib.matrix_multiply.restype = None
        self.lib.matrix_multiply(out,
                                 m1, ctypes.byref(nrows1), ctypes.byref(ncols1),
                                 m2, ctypes.byref(nrows2), ctypes.byref(ncols2))

        return [[out[c][r] for c in range(ncols2.value)] for r in range(nrows1.value)]
