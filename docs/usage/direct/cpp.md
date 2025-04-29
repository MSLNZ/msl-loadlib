# C++  {: #direct-cpp }

Load the example 64-bit C++ library in 64-bit Python. *To load the 32-bit library in 32-bit Python use `"cpp_lib32"` as the filename.*

!!! tip
    If the file extension is not specified, a default extension, `.dll` (Windows), `.so` (Linux) or `.dylib` (macOS) is used.

## Example

Load the example [C++ library][cpp-lib]

<!-- invisible-code-block: pycon
>>> SKIP_IF_32BIT() or SKIP_IF_MACOS_ARM64()

-->

```pycon
>>> from msl.loadlib import LoadLibrary
>>> from msl.examples.loadlib import EXAMPLES_DIR
>>> cpp = LoadLibrary(EXAMPLES_DIR + "/cpp_lib64")

```

By default, [ctypes][]{:target="_blank"} treats all input argument types and the return type of a library function to be a [c_int][ctypes.c_int]{:target="_blank"}. Therefore, the [argtypes][ctypes-specifying-required-argument-types]{:target="_blank"} and the [restype][ctypes-return-types]{:target="_blank"} should be defined for each function in the library. A few examples for the [C++ library][cpp-lib] are shown below

```pycon
>>> from ctypes import c_char_p, c_float, c_int32
>>> cpp.lib.subtract.argtypes = [c_float, c_float]
>>> cpp.lib.subtract.restype = c_float
>>> cpp.lib.reverse_string_v1.argtypes = [c_char_p, c_int32, c_char_p]
>>> cpp.lib.reverse_string_v1.restype = None

```

Call the `add` function to calculate the sum of two integers

```pycon
>>> cpp.lib.add(1, 2)
3

```

Call the `subtract` function to calculate the difference between two floats

```pycon
>>> cpp.lib.subtract(7.1, 2.1)
5.0

```

Call the `reverse_string_v1` function to reverse the characters in a byte string. Python manages the memory of the reversed sting by creating a string buffer of the necessary length

```pycon
>>> from ctypes import create_string_buffer
>>> original = b"olleh"
>>> reverse = create_string_buffer(len(original))
>>> cpp.lib.reverse_string_v1(original, len(original), reverse)
>>> reverse.raw.decode()
'hello'

```

## C++ Source Code {: #cpp-lib }

??? example "cpp_lib"

    === "cpp_lib.cpp"
        ```cpp
        --8<-- "src/msl/examples/loadlib/cpp_lib.cpp"
        ```

    === "cpp_lib.h"
        ```cpp
        --8<-- "src/msl/examples/loadlib/cpp_lib.h"
        ```
