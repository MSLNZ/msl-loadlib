# MSL-LoadLib

[![CI Status](https://github.com/MSLNZ/msl-loadlib/actions/workflows/ci.yml/badge.svg)](https://github.com/MSLNZ/msl-loadlib/actions/workflows/ci.yml)
[![Docs Status](https://github.com/MSLNZ/msl-loadlib/actions/workflows/docs.yml/badge.svg)](https://github.com/MSLNZ/msl-loadlib/actions/workflows/docs.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/msl-loadlib?logo=pypi&logoColor=gold&label=PyPI&color=blue)](https://pypi.org/project/msl-loadlib/)

This package loads a library in Python. It is basically just a thin wrapper around [ctypes] (for libraries that use the `__cdecl` or `__stdcall` calling convention), [Python.NET] (for libraries that use Microsoft .NET, `CLR`), [Py4J] (for Java `.jar` or `.class` files) and [comtypes] (for libraries that use the [Component Object Model] or [ActiveX]).

However, the primary advantage is that it is possible to communicate with a 32-bit library from 64-bit Python.

`msl-loadlib` is a pure-python package, but [Python.NET] depends on the .NET Common Language Runtime (CLR) on Windows and Mono Runtime on Linux/macOS, and [Py4J] depends on having a [Java Virtual Machine] installed.

## Install
`msl-loadlib` is available for installation via the [Python Package Index](https://pypi.org/project/msl-loadlib/)

```console
pip install msl-loadlib
```

Optional dependencies:

* [Python.NET]
* [Py4J]
* [comtypes]



To set up your environment on Linux, please follow the instructions on the [prerequisites](https://mslnz.github.io/msl-loadlib/latest/install/#linux) section of the documentation.

## Examples
If you are loading a 64-bit library in 64-bit Python (or a 32-bit library in 32-bit Python), then you can directly load the library using `LoadLibrary`.

*The following examples load a 64-bit library in a 64-bit Python interpreter. If you are using a 32-bit Python interpreter replace `64` with `32` in the filename.*

Import the `LoadLibrary` class and the directory where the example libraries are located

<!-- invisible-code-block: pycon
>>> SKIP_README_ALL()

-->

```pycon
>>> from msl.loadlib import LoadLibrary
>>> from msl.examples.loadlib import EXAMPLES_DIR

```

If the file extension is not included then a default extension, `.dll` (Windows), `.so` (Linux) or `.dylib` (macOS), is used.

Load the [example C++](https://github.com/MSLNZ/msl-loadlib/blob/main/src/msl/examples/loadlib/cpp_lib.cpp) library and call the `add` function

```pycon
>>> cpp = LoadLibrary(EXAMPLES_DIR / "cpp_lib64")
>>> cpp.lib.add(1, 2)
3

```

Load the [example FORTRAN](https://github.com/MSLNZ/msl-loadlib/blob/main/src/msl/examples/loadlib/fortran_lib.f90) library and call the `factorial` function

```pycon
>>> fortran = LoadLibrary(EXAMPLES_DIR / "fortran_lib64")

```

With a FORTRAN library you must pass values by reference using [ctypes], and, since the returned value is not of type `c_int` we must configure [ctypes] for a value of type `c_double` to be returned

```pycon
>>> from ctypes import byref, c_int, c_double
>>> fortran.lib.factorial.restype = c_double
>>> fortran.lib.factorial(byref(c_int(37)))
1.3763753091226343e+43

```

Load the [example Java](https://github.com/MSLNZ/msl-loadlib/blob/main/src/msl/examples/loadlib/Trig.java) byte code and call the `cos` function

```pycon
>>> java = LoadLibrary(EXAMPLES_DIR / "Trig.class")
>>> java.lib.Trig.cos(1.234)
0.33046510807172985

```

Python interacts with the [Java Virtual Machine] via a local network socket and therefore the connection must be closed when you are done using the Java library

```pycon
>>> java.gateway.shutdown()

```

Load the [example .NET](https://github.com/MSLNZ/msl-loadlib/blob/main/src/msl/examples/loadlib/dotnet_lib.cs) library and call the `reverse_string` function, we must specify that the library type is a .NET library by including the `"net"` argument

<!-- invisible-code-block: pycon
>>> SKIP_README_DOTNET()

-->

```pycon
>>> net = LoadLibrary(EXAMPLES_DIR / "dotnet_lib64.dll", "net")
>>> net.lib.StringManipulation().reverse_string("abcdefghijklmnopqrstuvwxyz")
'zyxwvutsrqponmlkjihgfedcba'

```

<!-- invisible-code-block: pycon
# https://github.com/pythonnet/pythonnet/issues/1683
>>> net.cleanup()

-->

To load a [Component Object Model] (COM) library pass in the library's Program ID. *NOTE: This example will only work on Windows.*

Here we load the [FileSystemObject](https://learn.microsoft.com/en-us/office/vba/language/reference/user-interface-help/filesystemobject-object) library and include the `"com"` argument to indicate that it is a COM library.

<!-- invisible-code-block: pycon
>>> SKIP_README_COM()

-->

```pycon
>>> com = LoadLibrary("Scripting.FileSystemObject", "com")

```

We then use the library to create, edit and close a text file

```pycon
>>> f = com.lib.CreateTextFile("a_new_file.txt")
>>> f.WriteLine("This is a test")
0
>>> f.Close()
0

```

<!-- invisible-code-block: pycon
>>> import os
>>> os.remove("a_new_file.txt")

-->

[Inter-process communication] is used to access a 32-bit library from a module that is running within a 64-bit Python interpreter. The procedure uses a client-server protocol where the client is a subclass of ``msl.loadlib.Client64`` and the server is a subclass of ``msl.loadlib.Server32``. See the [examples](https://mslnz.github.io/msl-loadlib/latest/examples) for examples on how to implement [Inter-process communication].

## Documentation
The documentation for `msl-loadlib` can be found [here](https://mslnz.github.io/msl-loadlib/latest/).

[ctypes]: https://docs.python.org/3/library/ctypes.html
[Python.NET]: https://pythonnet.github.io/
[Py4J]: https://www.py4j.org/
[Inter-process communication]: https://en.wikipedia.org/wiki/Inter-process_communication
[Java Virtual Machine]: https://en.wikipedia.org/wiki/Java_virtual_machine
[comtypes]: https://comtypes.readthedocs.io/en/stable/index.html
[Component Object Model]: https://learn.microsoft.com/en-us/windows/win32/com/component-object-model--com--portal
[ActiveX]: https://learn.microsoft.com/en-us/windows/win32/com/activex-controls
