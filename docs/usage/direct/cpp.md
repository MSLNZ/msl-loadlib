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

Call the `add` function to calculate the sum of two integers

```pycon
>>> cpp.lib.add(1, 2)
3

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
