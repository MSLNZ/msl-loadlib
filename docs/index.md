# Overview

This package loads a library in Python. It is basically just a thin wrapper around [ctypes][]{:target="_blank"} (for libraries that use the `__cdecl` or `__stdcall` calling convention), [Python.NET]{:target="_blank"} (for libraries that use .NET, `CLR`), [Py4J]{:target="_blank"} (for Java `.jar` or `.class` files) and [comtypes]{:target="_blank"} (for libraries that use the [Component Object Model]{:target="_blank"} or [ActiveX]{:target="_blank"}).

However, the primary advantage is that it is possible to communicate with a 32-bit library from 64-bit Python. For various reasons, mainly to do with the differences in pointer sizes, it is not possible to load a 32-bit library (e.g., `.dll`, `.so`, `.dylib` files) in a 64-bit process, and vice versa. This package contains a [Server32][] class that hosts a 32-bit library and a [Client64][] class that sends requests to the server to communicate with the 32-bit library as a form of [inter-process communication]{:target="_blank"}.

[ActiveX]: https://learn.microsoft.com/en-us/windows/win32/com/activex-controls
[Component Object Model]: https://learn.microsoft.com/en-us/windows/win32/com/component-object-model--com--portal
[comtypes]: https://comtypes.readthedocs.io/en/stable/index.html
[inter-process communication]: https://en.wikipedia.org/wiki/Inter-process_communication
[Py4J]: https://www.py4j.org/
[Python.NET]: https://pythonnet.github.io/
