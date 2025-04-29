# FORTRAN {: #ipc-fortran }

This example shows how to access a 32-bit FORTRAN library from 64-bit Python. [Fortran32][msl.examples.loadlib.fortran32.Fortran32] is the 32-bit server and [Fortran64][msl.examples.loadlib.fortran64.Fortran64] is the 64-bit client. The source code of the FORTRAN program is available [here][fortran-lib].

!!! attention
    If you have issues running the example make sure that you have the [prerequisites][] installed.

!!! important
    By default, [ctypes][]{:target="_blank"} expects that a [c_int][ctypes.c_int]{:target="_blank"} data type is returned from the library call. If the returned value from the library is not a [c_int][ctypes.c_int]{:target="_blank"} then you must redefine the ctypes [restype][ctypes-return-types]{:target="_blank"} value to be the appropriate data type. Also, the input arguments must be passed [by reference][ctypes.byref]{:target="_blank"}. The [Fortran32][msl.examples.loadlib.fortran32.Fortran32] class shows various examples of passing arguments by reference and defining the [restype][ctypes-return-types]{:target="_blank"} value.

Create a [Fortran64][msl.examples.loadlib.fortran64.Fortran64] client to communicate with the 32-bit [fortran_lib32][fortran-lib] library

<!-- invisible-code-block: pycon
>>> SKIP_IF_MACOS()

-->

```pycon
>>> from msl.examples.loadlib import Fortran64
>>> f = Fortran64()

```

## Numeric types {: #ipc-fortran-numerics }

Add two `int8` values, see [Fortran64.sum_8bit][msl.examples.loadlib.fortran64.Fortran64.sum_8bit]

```pycon
>>> f.sum_8bit(-50, 110)
60

```

Add two `int16` values, see [Fortran64.sum_16bit][msl.examples.loadlib.fortran64.Fortran64.sum_16bit]

```pycon
>>> f.sum_16bit(2**15-1, -1)
32766

```

Add two `int32` values, see [Fortran64.sum_32bit][msl.examples.loadlib.fortran64.Fortran64.sum_32bit]

```pycon
>>> f.sum_32bit(123456788, 1)
123456789

```

Add two `int64` values, see [Fortran64.sum_64bit][msl.examples.loadlib.fortran64.Fortran64.sum_64bit]

```pycon
>>> f.sum_64bit(2**63, -2**62)
4611686018427387904

```

Multiply two `float32` values, see [Fortran64.multiply_float32][msl.examples.loadlib.fortran64.Fortran64.multiply_float32]

```pycon
>>> f.multiply_float32(2.0, 3.0)
6.0

```

Multiply two `float64` values, see [Fortran64.multiply_float64][msl.examples.loadlib.fortran64.Fortran64.multiply_float64]

```pycon
>>> f.multiply_float64(1e30, 2e3)
2.00000000000...e+33

```

Check if a value is positive, see [Fortran64.is_positive][msl.examples.loadlib.fortran64.Fortran64.is_positive]

```pycon
>>> f.is_positive(1.0)
True
>>> f.is_positive(-0.1)
False

```

Add or subtract two integers, see [Fortran64.add_or_subtract][msl.examples.loadlib.fortran64.Fortran64.add_or_subtract]

```pycon
>>> f.add_or_subtract(1000, 2000, True)
3000
>>> f.add_or_subtract(1000, 2000, False)
-1000

```

Calculate the n'th factorial, see [Fortran64.factorial][msl.examples.loadlib.fortran64.Fortran64.factorial]

```pycon
>>> f.factorial(0)
1.0
>>> f.factorial(127)
3.012660018457658e+213

```

Compute the Bessel function of the first kind of order 0, see [Fortran64.besselJ0][msl.examples.loadlib.fortran64.Fortran64.besselJ0]

```pycon
>>> f.besselJ0(8.6)
0.0146229912787412...

```

## Arrays {: #ipc-fortran-arrays }

Calculate the standard deviation of a list of values, see [Fortran64.standard_deviation][msl.examples.loadlib.fortran64.Fortran64.standard_deviation]

```pycon
>>> f.standard_deviation([float(val) for val in range(1,10)])
2.73861278752583...

```

Add two 1D arrays, see [Fortran64.add_1d_arrays][msl.examples.loadlib.fortran64.Fortran64.add_1d_arrays]

```pycon
>>> a = [float(val) for val in range(1, 10)]
>>> b = [0.5*val for val in range(1, 10)]
>>> a
[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
>>> b
[0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
>>> f.add_1d_arrays(a, b)
[1.5, 3.0, 4.5, 6.0, 7.5, 9.0, 10.5, 12.0, 13.5]

```

Multiply two matrices, see [Fortran64.matrix_multiply][msl.examples.loadlib.fortran64.Fortran64.matrix_multiply]

```pycon
>>> m1 = [[1, 2, 3], [4, 5, 6]]
>>> m2 = [[1, 2], [3, 4], [5, 6]]
>>> f.matrix_multiply(m1, m2)
[[22.0, 28.0], [49.0, 64.0]]

```

## Strings {: #ipc-fortran-strings }

Reverse a string, see [Fortran64.reverse_string][msl.examples.loadlib.fortran64.Fortran64.reverse_string]

```pycon
>>> f.reverse_string("hello world!")
'!dlrow olleh'

```

You have access to the server's `stdout` and `stderr` streams when you shut down the server

```pycon
>>> stdout, stderr = f.shutdown_server32()

```
