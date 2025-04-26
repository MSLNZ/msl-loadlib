# Examples

The following classes illustrate how the [Client-Server][] communication works.

Classes that end in *32* contain a class that is a subclass of [Server32][]. This class is a wrapper around a 32-bit library and is hosted on a 32-bit server. Viewing the source code of this class may be useful to see how different data types (e.g., strings, numbers, arrays) are passed between Python and a function in the library.

Classes that end in *64* contain a class that is a subclass of [Client64][]. This class sends a request to the corresponding [Server32][] subclass to communicate with the 32-bit library.

* [Cpp32][]
* [Cpp64][]
* [DotNet32][]
* [DotNet64][]
* [Echo32][]
* [Echo64][]
* [Fortran32][]
* [Fortran64][]
* [Kernel32][]
* [Kernel64][]
* [Labview32][]
* [Labview64][]
