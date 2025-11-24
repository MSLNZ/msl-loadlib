# Install

`msl-loadlib` is available for installation via the [Python Package Index]{:target="_blank"}

```console
pip install msl-loadlib
```

## Optional dependencies

* [Python.NET]{:target="_blank"}
* [Py4J]{:target="_blank"}
* [comtypes]{:target="_blank"}

You can install `msl-loadlib` and [Python.NET]{:target="_blank"} using,

```console
pip install msl-loadlib[clr]
```

`msl-loadlib` and [Py4J]{:target="_blank"},

```console
pip install msl-loadlib[java]
```

`msl-loadlib` and [comtypes]{:target="_blank"},

```console
pip install msl-loadlib[com]
```

or `msl-loadlib` and all optional dependencies

```console
pip install msl-loadlib[all]
```

## Compatibility
* The 32-bit server is built into a [frozen]{:target="_blank"} executable for Windows and Linux (glibc).
* You may also [create a custom 32-bit server][refreeze].

## Prerequisites

### Windows

64-bit Windows already comes with [WoW64]{:target="_blank"} to run 32-bit software and therefore no prerequisites are required to load 32-bit libraries. However, the library might have its own dependencies, such as a particular Visual C++ Redistributable, that may need to be installed.

If you need to load a .NET library, you must install [Python.NET]{:target="_blank"} (see also [Configure a .NET runtime][config-runtime]).

```console
pip install pythonnet
```

If you need to load a Java library (i.e., a `.jar` or `.class` file), you must install [Py4J]{:target="_blank"},

```console
pip install py4j
```

a [Java Runtime Environment]{:target="_blank"}, and ensure that the `java` executable is available on the [PATH]{:target="_blank"} environment variable. For example, the following should return the version of Java that is installed

```console
> java -version
java version "25.0.1" 2025-10-21 LTS
Java(TM) SE Runtime Environment (build 25.0.1+8-LTS-27)
Java HotSpot(TM) 64-Bit Server VM (build 25.0.1+8-LTS-27, mixed mode, sharing)
```

If you need to load a [Component Object Model]{:target="_blank"} or an [ActiveX]{:target="_blank"} library you must install [comtypes]{:target="_blank"}

```console
pip install comtypes
```

!!! tip "Managing library dependencies"
    When loading a library it is vital that all dependencies of the library are also on the computer and that the directory that the dependencies are located in is available on the [PATH]{:target="_blank"} variable (and possibly you may need to add a directory with [os.add_dll_directory][]{:target="_blank"}). A helpful utility to determine the dependencies of a library on Windows is [Dependencies]{:target="_blank"} (which is a modern [Dependency Walker]{:target="_blank"}). Microsoft also provides the [DUMPBIN]{:target="_blank"} tool. For finding the dependencies of a .NET library the [Dependency Walker for .NET]{:target="_blank"} may also be helpful.

### Linux

Before using `msl-loadlib` on Debian-based Linux distributions, the following packages are required. For other distributions, use the appropriate system package manager (e.g., *yum*) and the equivalent command.

Install the packages that are required to load 32-bit and 64-bit C/C++ and FORTRAN libraries

!!! attention
    The following packages are required to run the examples that are included with `msl-loadlib`. The dependencies for the C/C++ or FORTRAN library that you want to load may be different.

```console
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install g++ gfortran libgfortran5 zlib1g:i386 libstdc++6:i386 libgfortran5:i386
```

The following ensures that the [ss]{:target="_blank"} command is available

```console
sudo apt install iproute2
```

If you need to load a .NET library, you must install either the [Mono]{:target="_blank"} or [.NET Core]{:target="_blank"} runtime and [Python.NET]{:target="_blank"} (see also [Configure a .NET runtime][config-runtime]).

```console
pip3 install pythonnet
```

!!! important
    As of version 0.10.0 of `msl-loadlib`, `pythonnet` is no longer installed on the 32-bit server for Linux. [Mono]{:target="_blank"} can load both 32-bit and 64-bit libraries on 64-bit Linux and therefore a 32-bit .NET library can be loaded directly via [LoadLibrary][msl.loadlib.load_library.LoadLibrary] on 64-bit Linux.

If you need to load a Java library (i.e., a `.jar` or `.class` file), you must install [Py4J]{:target="_blank"},

```console
pip3 install py4j
```

and a [Java Runtime Environment]{:target="_blank"}

```console
sudo apt install default-jre
```

!!! tip
    When loading a library it is vital that all dependencies of the library are also on the computer and that the directory that the dependency is located in is available on the [PATH]{:target="_blank"} variable. A helpful utility to determine the dependencies of a library on Unix is [ldd]{:target="_blank"}.

### macOS

The 32-bit server has not been created for macOS; however, the [LoadLibrary][msl.loadlib.load_library.LoadLibrary] class can be used to load a library that uses the `__cdecl` calling convention that is the same bitness as the Python interpreter, a .NET library or a Java library.

The following assumes that you are using [Homebrew]{:target="_blank"} as your package manager.

!!! tip
    It is recommended to update [Homebrew]{:target="_blank"} before installing packages with `brew update`

To load a C/C++ or FORTRAN library install gcc (which includes gfortran)

```console
brew install gcc
```

If you need to load a .NET library, you must install either the [Mono]{:target="_blank"} or [.NET Core]{:target="_blank"} runtime and [Python.NET]{:target="_blank"} (see also [Configure a .NET runtime][config-runtime]).

```console
brew install mono
```

and [Python.NET]{:target="_blank"}

```console
pip3 install pythonnet
```

If you need to load a Java library (i.e., a `.jar` or `.class` file), you must install [Py4J]{:target="_blank"},

```console
pip3 install py4j
```

and a [Java Runtime Environment]{:target="_blank"}

```console
brew cask install java
```

[ActiveX]: https://learn.microsoft.com/en-us/windows/win32/com/activex-controls
[Component Object Model]: https://learn.microsoft.com/en-us/windows/win32/com/component-object-model--com--portal
[comtypes]: https://comtypes.readthedocs.io/en/stable/index.html
[Dependencies]: https://github.com/lucasg/Dependencies
[Dependency Walker]: https://www.dependencywalker.com/
[Dependency Walker for .NET]: https://github.com/isindicic/DependencyWalker.Net
[DUMPBIN]: https://learn.microsoft.com/en-us/cpp/build/reference/dumpbin-reference?view=msvc-170
[frozen]: https://pyinstaller.readthedocs.io/en/stable/
[Homebrew]: https://brew.sh/
[inter-process communication]: https://en.wikipedia.org/wiki/Inter-process_communication
[Java Runtime Environment]: https://www.java.com/en/download/manual.jsp
[ldd]: https://man7.org/linux/man-pages/man1/ldd.1.html
[Mono]: https://www.mono-project.com/download/stable/
[.NET Core]: https://dotnet.microsoft.com/en-us/download/dotnet/latest/runtime
[PATH]: https://en.wikipedia.org/wiki/PATH_(variable)
[Py4J]: https://www.py4j.org/
[Python.NET]: https://pythonnet.github.io/
[Python Package Index]: https://pypi.org/project/msl-loadlib/
[ss]: https://man7.org/linux/man-pages/man8/ss.8.html
[WoW64]: https://en.wikipedia.org/wiki/WoW64
