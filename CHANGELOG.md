# Release Notes

---

## unreleased

***Added:***

- `Client64` now accepts `host=None` which will mock the connection to the server
- `freeze32` console script to create a new 32-bit server
- support for Python 3.12 and 3.13
- type annotations

***Changed:***

- convert to an implicit namespace package ([PEP-420](https://peps.python.org/pep-0420/))
- the `requires_pythonnet` and `requires_comtypes` arguments to `freeze_server32.main()` were removed and the `imports`, `data` `skip_32bit_check`, `keep_spec` and `keep_tk` arguments were added
- all constants (e.g., `IS_WINDOWS`) were moved to a (private) `_constants.py` file
- data type of `EXAMPLES_DIR` and the return type from `Server32.examples_dir()` changed from [str][] to [Path][pathlib.Path]

***Removed:***

- support for Python 2.7, 3.5, 3.6 and 3.7
- the deprecated `quiet` parameter

## 0.10.0 (2023-06-16)
*This release will be the last to support Python 2.7, 3.5, 3.6 and 3.7*

The 32-bit server is frozen with the following versions

- `server32-windows.exe` &ndash; Python 3.11.4, pythonnet 3.0.1, comtypes 1.2.0
- `server32-linux` &ndash; Python 3.11.4 (built with GLIBC 2.27)

***Added:***

- can now specify the destination directory when freezing the 32-bit server
- the `server32_dir` keyword argument to `Client64` (fixes issue [#35](https://github.com/MSLNZ/msl-loadlib/issues/35))
- support for Python 3.10 and 3.11
- `LoadLibrary` and `Client64` can now be used as a context manager ([with statement](https://docs.python.org/3/reference/compound_stmts.html#with))
- `LoadLibrary.cleanup()` method
- `~/.local/share/py4j` to the search paths when looking for the `py4j<version>.jar` file

***Changed:***

- `utils.is_port_in_use()` only checks TCP ports and it uses the `ss` command instead of `netstat` on linux
- the example libraries for FORTRAN now depend on `libgfortran5` on linux

***Fixed:***

- issue [#31](https://github.com/MSLNZ/msl-loadlib/issues/31) &ndash; suppress console popups when using `pythonw.exe`
- issue [#24](https://github.com/MSLNZ/msl-loadlib/issues/24) &ndash; starting the 32-bit server could block forever by not honouring the timeout

## 0.9.0 (2021-05-13)

The 32-bit server is frozen with the following versions

- `server32-windows.exe` &ndash; Python 3.7.10, pythonnet 2.5.2, comtypes 1.1.10
- `server32-linux` &ndash; Python 3.7.10, pythonnet 2.4.0

***Added:***

- support for loading an ActiveX library
- the following static methods to `Server32` &ndash; `remove_site_packages_64bit`, `is_interpreter`, `examples_dir`
- the `utils.generate_com_wrapper` function

***Changed:***

- the `sys.coinit_flags` attribute is now set to ``COINIT_MULTITHREADED`` (only if this attribute was not already defined prior to importing `msl.loadlib`)

***Fixed:***

- `Client64.__del__` could have written a warning to stderr indicating that no `self._conn` attribute existed
- `sys:1: ResourceWarning: unclosed file <_io.BufferedReader name=...>` warnings could be written to stderr when a `Client64` object is destroyed
- issue [#23](https://github.com/MSLNZ/msl-loadlib/issues/23) &ndash; the `useLegacyV2RuntimeActivationPolicy` property was no longer created

## 0.8.0 (2021-02-20)

The 32-bit server is frozen with the following versions

- `server32-windows.exe` &ndash; Python 3.7.10, pythonnet 2.5.2 and comtypes 1.1.8
- `server32-linux` &ndash; Python 3.7.10 and pythonnet 2.4.0

***Added:***

- support for Python 3.9
- the `protocol` keyword argument to `Client64`
- the ability to request non-callable attributes from the 32-bit server class (e.g., methods that use the `@property` decorator and class/instance variables)

***Changed:***

- call `clr.AddReference` before `clr.System.Reflection.Assembly.LoadFile` when loading a .NET library
- use PIPE's for `stdout` and `stderr` for the 32-bit server subprocess and for the py4j `GatewayServer`
- `Client64.shutdown_server32` now returns the `(stdout, stderr)` streams from the 32-bit server subprocess
- the `quiet` keyword argument for `Client64` is now deprecated

***Fixed:***

- issue [#21](https://github.com/MSLNZ/msl-loadlib/issues/21) &ndash; an `UnsupportedOperation: fileno` exception was raised when running within the Spyder IDE

***Removed:***

- `cygwin` from the `IS_WINDOWS` check

## 0.7.0 (2020-03-17)

The 32-bit server is frozen with the following versions

- `server32-windows.exe` &ndash; Python 3.7.7, pythonnet 2.4.0 and comtypes 1.1.7
- `server32-linux` &ndash; Python 3.7.7 and pythonnet 2.4.0

***Added:***

- support for Python 3.8
- compiled the C++ and FORTRAN examples for 64-bit macOS

***Changed:***

- use `__package__` as the logger name
- renamed `utils.port_in_use()` to `utils.is_port_in_use()` and added support for checking the status of a port in macOS
- changes to how a .NET library is loaded: include the System namespace by default, do not automatically create a class instance

***Removed:***

- support for Python 3.4

## 0.6.0 (2019-05-07)

The 32-bit server is frozen with the following versions

- `server32-windows.exe` &ndash; Python 3.7.3, pythonnet 2.4.0 and comtypes 1.1.7
- `server32-linux` &ndash; Python 3.7.3 and pythonnet 2.4.0

***Added:***

- a `shutdown_handler()` method to `Server32` (PR [#19](https://github.com/MSLNZ/msl-loadlib/pull/19))
- a section to the docs that explains how to re-freeze the 32-bit server
- a `kill_timeout` keyword argument to `Client64.shutdown_server32()`
- the `rpc_timeout` keyword argument to `Client64` (thanks to @fake-name)
- search `HKEY_CLASSES_ROOT\\Wow6432Node\\CLSID` in the Windows Registry for additional COM `ProgID`'s
- `extras_require` parameter to `setup.py` with keys: `clr`, `java`, `com`, `all`

***Changed:***

- rename the optional `-asp` and `-aep` command line arguments to be `-s` and `-e` respectively
- the current working directory where the 64-bit Python interpreter was executed from is now automatically appended to `os.environ['PATH']` on the 32-bit server
- `freeze_server32.py` uses an `ArgumentParser` instead of directly reading from `sys.argv`

***Fixed:***

- use `sys.executable -m PyInstaller` to create the 32-bit server (cherry picked from PR [#18](https://github.com/MSLNZ/msl-loadlib/pull/18))
- the 32-bit server prints error messages to `sys.stderr` instead of `sys.stdout`
- issue [#15](https://github.com/MSLNZ/msl-loadlib/issues/15) &ndash; wait for the subprocess that starts the 32-bit server to terminate and set a value for the `returncode`
- issue [#14](https://github.com/MSLNZ/msl-loadlib/issues/14) &ndash; use `os.kill` to stop the 32-bit server if it won't stop after `kill_timeout` seconds

## 0.5.0 (2019-01-06)

The 32-bit server is frozen with the following versions

- `server32-windows.exe` &ndash; Python 3.6.8, pythonnet 2.3.0 and comtypes 1.1.7
- `server32-linux` &ndash; Python 3.6.8 and pythonnet 2.3.0

***Added:***

- support for loading a Component Object Model (COM) library on Windows
- the `requires_pythonnet` and `requires_comtypes` kwargs to `freeze_server32.main()`
- `"clr"` as an alias for `"net"` for the `libtype` parameter in `LoadLibrary`
- the `utils.get_com_info()` function
- support for unicode paths in Python 2
- examples for working with numpy arrays and C++ structs

***Changed:***

- if loading a .NET assembly succeeds but calling `GetTypes()` fails then a detailed error message is logged rather than raising the exception - the value of `lib` will be `None`
- the default timeout value when waiting for the 32-bit server to start is now 10 seconds
- the `Client64` class now raises `Server32Error` if the 32-bit server raises an exception
- the `Client64` class now inherits from `object` and the reference to `HTTPConnection` is now a property value
- the `__repr__` methods no longer include the id as a hex number

***Fixed:***

- set `sys.stdout = io.StringIO()` if `quiet=True` on the server

## 0.4.1 (2018-08-24)

The 32-bit server is frozen with the following versions

- `server32-windows.exe` &ndash; Python 3.6.6 and pythonnet 2.3.0
- `server32-linux` &ndash; Python 3.6.6 and pythonnet 2.3.0

***Added:***

- the `version_info` namedtuple now includes a *releaselevel*
- support for Python 3.7

***Fixed:***

- issue [#11](https://github.com/MSLNZ/msl-loadlib/issues/11)
- `utils.wait_for_server()` raised `NameError: name 'TimeoutError' is not defined` for Python 2.7
- `utils.port_in_use()` raised `UnicodeDecodeError` (PR [#9](https://github.com/MSLNZ/msl-loadlib/pull/9))
- `setup.py` is now also compatible with Sphinx 1.7+

***Changed:***

- pythonnet is now an optional dependency on Windows and py4j is now optional for all OS
- rename `Dummy` example to `Echo`

***Removed:***

- support for Python 3.3

## 0.4.0 (2018-02-28)

The 32-bit server is frozen with the following versions

- `server32-windows.exe` &ndash; Python 3.6.4 and pythonnet 2.3.0
- `server32-linux` &ndash; Python 3.6.4 and pythonnet 2.3.0

***Added:***

- [Py4J](https://www.py4j.org/) wrapper for loading `.jar` and `.class` Java files
- example on how to load a library that was built with LabVIEW

***Fixed:***

- issue [#8](https://github.com/MSLNZ/msl-loadlib/issues/8)
- issue [#7](https://github.com/MSLNZ/msl-loadlib/issues/7)
- `AttributeError("'LoadLibrary' object has no attribute '_lib'")` could be raised in `__repr__`

***Changed:***

- rename `DotNetContainer` to `DotNet`
- use `socket.socket.bind` to select an available port instead of checking of calling `utils.port_in_use`
- moved the static methods to the `utils` module:
    + Client64.port_in_use &#8594; utils.port_in_use
    + Client64.get_available_port &#8594; utils.get_available_port
    + Client64.wait_for_server &#8594; utils.wait_for_server
    + LoadLibrary.check_dot_net_config &#8594; utils.check_dot_net_config
    + LoadLibrary.is_pythonnet_installed &#8594; utils.is_pythonnet_installed

## 0.3.2 (2017-10-18)

The 32-bit server is frozen with the following versions

- `server32-windows.exe` &ndash; Python 3.6.3 and pythonnet 2.3.0
- `server32-linux` &ndash; Python 3.6.3 and pythonnet 2.3.0

***Added:***

- include `os.environ['PATH']` as a search path when loading a library
- support that the package can now be installed by `pip install msl-loadlib`

***Fixed:***

- remove `sys.getsitepackages()` error for virtualenv (issue [#5](https://github.com/MSLNZ/msl-loadlib/issues/5))
- `RecursionError` when freezing freeze_server32.py with PyInstaller 3.3
- replaced `FileNotFoundError` with `IOError` (for Python 2.7 support)
- recompile `cpp_lib*.dll` and `fortran_lib*.dll` to not depend on external dependencies

## 0.3.1 (2017-05-15)

- fix ReadTheDocs build error &ndash; AttributeError: module 'site' has no attribute 'getsitepackages'
- strip whitespace from append_sys_path and append_environ_path
- make pythonnet a required dependency only for Windows

## 0.3.0 (2017-05-09)
*NOTE: This release breaks backward compatibility*

- can now pass `**kwargs` from the `Client64` constructor to the `Server32`-subclass constructor
- new command line arguments for starting the 32-bit server: `--kwargs`, `--append_environ_path`
- renamed the `--append_path` command line argument to `--append_sys_path`
- `Server32.interactive_console()` works on Windows and Linux
- edit documentation (thanks to @karna48 for the pull request)

## 0.2.3 (2017-04-11)
- the frozen server32 executable (for Windows/Linux) now uses Python v3.6.1 and Python.NET v2.3.0
- include `ctypes.util.find_library` and `sys.path` when searching for a library

## 0.2.2 (2017-03-03)
- refreeze server32 executables

## 0.2.1 (2017-03-02)
- fix `releaselevel` bug

## 0.2.0 (2017-03-02)
- examples now working in Linux
- fix MSL namespace
- include all C# modules, classes and System.Type objects in the .NET loaded-library object
- create a custom C# library for the examples
- edit docstrings and documentation
- many bug fixes

## 0.1.0 (2017-02-15)
- Initial release
