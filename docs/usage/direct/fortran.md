# FORTRAN {: #direct-fortran }

Load a 64-bit FORTRAN library in 64-bit Python. *To load the 32-bit library in 32-bit Python use `"fortran_lib32"` as the filename.*

!!! tip
    If the file extension is not specified, a default extension, `.dll` (Windows), `.so` (Linux) or `.dylib` (macOS) is used.

## Example

Load the example [FORTRAN library][fortran-lib]

<!-- invisible-code-block: pycon
>>> SKIP_IF_32BIT() or SKIP_IF_MACOS_ARM64()

-->

```pycon
>>> from msl.loadlib import LoadLibrary
>>> from msl.examples.loadlib import EXAMPLES_DIR
>>> fortran = LoadLibrary(EXAMPLES_DIR + "/fortran_lib64")

```

Call the `factorial` function. With a FORTRAN library you must pass values by reference using [byref][ctypes.byref]{:target="_blank"} and since the returned value is not of type [c_int][ctypes.c_int]{:target="_blank"} the [restype][ctypes-return-types]{:target="_blank"} must be configured for a value of type [c_double][ctypes.c_double]{:target="_blank"} to be returned from the library function

```pycon
>>> from ctypes import byref, c_int, c_double
>>> fortran.lib.factorial.restype = c_double
>>> fortran.lib.factorial(byref(c_int(37)))
1.3763753091226343e+43

```

## FORTRAN Source Code {: #fortran-lib }

??? example "fortran_lib.f90"
    ```fortran
    --8<-- "src/msl/examples/loadlib/fortran_lib.f90"
    ```
