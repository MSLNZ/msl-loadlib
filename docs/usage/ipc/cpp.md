# C++ {: #ipc-cpp }

This example shows how to access a 32-bit C++ library from 64-bit Python. [Cpp32][msl.examples.loadlib.cpp32.Cpp32] is the 32-bit server and [Cpp64][msl.examples.loadlib.cpp64.Cpp64] is the 64-bit client.

The source code of the C++ program is available [here][cpp-lib].

!!! attention
    If you have issues running the example make sure that you have the [prerequisites][] installed.

!!! important
    By default, [ctypes][]{:target="_blank"} expects that a [ctypes.c_int][]{:target="_blank"} data type is returned from the library call. If the returned value from the library is not a [ctypes.c_int][]{:target="_blank"} then you must redefine the ctypes [restype][ctypes-return-types]{:target="_blank"} value to be the appropriate data type. The [Cpp32][msl.examples.loadlib.cpp32.Cpp32] class shows various examples of redefining the [restype][ctypes-return-types]{:target="_blank"} value.

Create a [Cpp64][msl.examples.loadlib.cpp64.Cpp64] client to communicate with the 32-bit library from 64-bit Python

<!-- invisible-code-block: pycon
>>> SKIP_IF_MACOS()

-->

```pycon
>>> from msl.examples.loadlib import Cpp64
>>> cpp = Cpp64()

```

## Numeric types {: #ipc-cpp-numerics }

Add two integers, see [Cpp64.add][msl.examples.loadlib.cpp64.Cpp64.add]

```pycon
>>> cpp.add(3, 14)
17

```

Subtract two C++ floating-point numbers, see [Cpp64.subtract][msl.examples.loadlib.cpp64.Cpp64.subtract]

```pycon
>>> cpp.subtract(43.2, 3.2)
40.0

```

Add or subtract two C++ double-precision numbers, see [Cpp64.add_or_subtract][msl.examples.loadlib.cpp64.Cpp64.add_or_subtract]

```pycon
>>> cpp.add_or_subtract(1.0, 2.0, True)
3.0
>>> cpp.add_or_subtract(1.0, 2.0, False)
-1.0

```

## Arrays {: #ipc-cpp-arrays }

Multiply a 1D array by a number, see [Cpp64.scalar_multiply][msl.examples.loadlib.cpp64.Cpp64.scalar_multiply]

!!! attention
    The [Cpp64.scalar_multiply][msl.examples.loadlib.cpp64.Cpp64.scalar_multiply] function takes a pointer to an array as an input argument, see the [source code][cpp-lib]. One cannot pass pointers from [Client64][] to [Server32][] because a 64-bit process cannot share the same memory space as a 32-bit process. All 32-bit pointers must be created (using [ctypes][]{:target="_blank"}) in the class that is a subclass of [Server32][] and only the **value** that is stored at that address can be returned to [Client64][] for use in the 64-bit program.

```pycon
>>> a = [float(val) for val in range(10)]
>>> cpp.scalar_multiply(2.0, a)
[0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0]

```

If you have a [numpy.ndarray][]{:target="_blank"} in 64-bit Python then you cannot pass the `ndarray` object to [Server32][] because the 32-bit server would need to load the `ndarray` in a 32-bit version of numpy (which is not included by default in the 32-bit server, but could be &ndash; see [refreeze][] for more details). To simplify the procedure you could convert the `ndarray` to a [list][]{:target="_blank"} using the [numpy.ndarray.tolist][]{:target="_blank"} method

```pycon
>>> import numpy as np
>>> a = np.arange(9.)
>>> cpp.scalar_multiply(3.1, a.tolist())
[0.0, 3.1, 6.2, 9.3, 12.4, 15.5, 18.6, 21.7, 24.8]

```

or you could use the builtin [array.array][]{:target="_blank"} class

```pycon
>>> from array import array
>>> b = array("d", a.tobytes())
>>> cpp.scalar_multiply(3.1, b)
[0.0, 3.1, 6.2, 9.3, 12.4, 15.5, 18.6, 21.7, 24.8]

```

If you want the returned value from `scalar_multiply` to be an `ndarray` use

```pycon
>>> np.array(cpp.scalar_multiply(3.1, b))
array([ 0. ,  3.1,  6.2,  9.3, 12.4, 15.5, 18.6, 21.7, 24.8])

```

## Strings {: #ipc-cpp-strings }

In this example the memory for the reversed string is allocated in Python, see [Cpp64.reverse_string_v1][msl.examples.loadlib.cpp64.Cpp64.reverse_string_v1]

```pycon
>>> cpp.reverse_string_v1("hello world!")
'!dlrow olleh'

```

In this example the memory for the reversed string is allocated in C++, see [Cpp64.reverse_string_v2][msl.examples.loadlib.cpp64.Cpp64.reverse_string_v2]

```pycon
>>> cpp.reverse_string_v2("uncertainty")
'ytniatrecnu'

```

## Structs {: #ipc-cpp-structs }

It is possible to [pickle][]{:target="_blank"} a [ctypes.Structure][]{:target="_blank"} and pass the
*struct* object between [Cpp64][msl.examples.loadlib.cpp64.Cpp64] and [Cpp32][msl.examples.loadlib.cpp32.Cpp32] provided that the *struct* is a **fixed size** in memory (i.e., the *struct* does not contain any pointers). If the *struct* contains pointers then you must create the *struct* within [Cpp32][msl.examples.loadlib.cpp32.Cpp32] and you can only pass the **values** of the *struct* back to [Cpp64][msl.examples.loadlib.cpp64.Cpp64].

The [source code][cpp-lib] of the C++ library contains the following structs

```cpp
struct Point {
    double x;
    double y;
};

struct FourPoints {
    Point points[4];
};

struct NPoints {
    int n;
    Point *points;
};
```

The [Cpp64.distance_4_points][msl.examples.loadlib.cpp64.Cpp64.distance_4_points] method uses the [FourPoints][msl.examples.loadlib.cpp32.FourPoints] struct to calculate the total distance connecting 4 [Point][msl.examples.loadlib.cpp32.Point] structs. Since the [FourPoints][msl.examples.loadlib.cpp32.FourPoints] struct is a **fixed size** it can be created in 64-bit Python, *pickled* and then *unpickled* in [Cpp32][msl.examples.loadlib.cpp32.Cpp32]

```pycon
>>> from msl.examples.loadlib import FourPoints
>>> fp = FourPoints((0, 0), (0, 1), (1, 1), (1, 0))
>>> cpp.distance_4_points(fp)
4.0

```

The [Cpp32.circumference][msl.examples.loadlib.cpp32.Cpp32.circumference] method uses the [NPoints][msl.examples.loadlib.cpp32.NPoints] struct to calculate the circumference of a circle using *n* [Point][msl.examples.loadlib.cpp32.Point] structs. Since the [NPoints][msl.examples.loadlib.cpp32.NPoints] struct is
**not a fixed size** it must be created in the [Cpp32.circumference][msl.examples.loadlib.cpp32.Cpp32.circumference] method. The [Cpp64.circumference][msl.examples.loadlib.cpp64.Cpp64.circumference] method takes the values of the *radius* and *n* as input arguments to pass to the [Cpp32.circumference][msl.examples.loadlib.cpp32.Cpp32.circumference] method.

```pycon
>>> for i in range(16):
...     print(cpp.circumference(0.5, 2**i))
...
0.0
2.0
2.828427124746...
3.061467458920...
3.121445152258...
3.136548490545...
3.140331156954...
3.141277250932...
3.141513801144...
3.141572940367...
3.141587725277...
3.141591421511...
3.141592345569...
3.141592576584...
3.141592634337...
3.141592648775...

```

You have access to the server's `stdout` and `stderr` streams when you shut down the server

```pycon
>>> stdout, stderr = cpp.shutdown_server32()

```
