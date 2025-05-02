# Directly loading a library {: #direct }

If you are loading a 64-bit library in 64-bit Python (or a 32-bit library in 32-bit Python) then you can directly load the library using the [LoadLibrary][msl.loadlib.load_library.LoadLibrary] class.

!!! attention
    See [Client-Server][client-server] if you want to load a 32-bit library in 64-bit Python.

The following examples are included with the `msl-loadlib` package:

* [C++][direct-cpp] &mdash; compiled in 32- and 64-bit Windows and Linux and in 64-bit macOS
* [FORTRAN][direct-fortran] &mdash; compiled in 32- and 64-bit Windows and Linux and in 64-bit macOS
* [.NET][direct-dotnet] &mdash; complied in 32- and 64-bit using Microsoft Visual Studio 2017
* [Java][direct-java] &mdash; platform and bitness independent since it runs in the [JVM]{:target="_blank"}
* [COM][direct-com] &mdash; load a [Component Object Model]{:target="_blank"} library on Windows
* [ActiveX][direct-activex] &mdash; illustrates how to load [ActiveX]{:target="_blank"} controls on Windows
* [Windows __stdcall][direct-stdcall] &mdash; a 32-bit library that uses the `__stdcall` calling convention
* [LabVIEW][direct-labview] &mdash; built using 32- and 64-bit LabVIEW on Windows

[Component Object Model]: https://learn.microsoft.com/en-us/windows/win32/com/component-object-model--com--portal
[JVM]: https://en.wikipedia.org/wiki/Java_virtual_machine
[ActiveX]: https://learn.microsoft.com/en-us/windows/win32/com/activex-controls
