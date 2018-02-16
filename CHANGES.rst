=========
Changelog
=========

Version 0.3.3 (in development)
==============================

Added
-----
* include a ``get_assembly_types`` keyword argument to the :class:`~msl.loadlib.load_library.LoadLibrary` class
* improved the error message when loading a .NET Assembly and pythonnet is not installed
* updated the documentation and the docstrings

Fixed
-----
* Issue `#8 <https://github.com/MSLNZ/msl-loadlib/issues/8>`_
* Issue `#7 <https://github.com/MSLNZ/msl-loadlib/issues/7>`_
* ``AttributeError("'LoadLibrary' object has no attribute '_lib'") raised in repr()``

Changed
-------
* use :meth:`~socket.socket.bind` to select an available port
  instead of checking if :meth:`~msl.loadlib.client64.Client64.port_in_use`

Version 0.3.2 (2017.10.18)
==========================

Added
-----
* include ``os.environ['PATH']`` as a search path when loading a shared library
* the frozen server32 executable (for Windows/Linux) now runs on Python 3.6.3
* support that the package can now be installed by ``pip install msl-loadlib``

Fixed
-----
* remove ``sys.getsitepackages()`` error for virtualenv (`issue #5 <https://github.com/MSLNZ/msl-loadlib/issues/5>`_)
* received ``RecursionError`` when freezing freeze_server32.py with PyInstaller 3.3
* replaced ``FileNotFoundError`` with ``IOError`` (for Python 2.7 support)
* recompile cpp_lib\*.dll and fortran_lib\*.dll to not depend on external dependencies

Version 0.3.1 (2017.05.15)
==========================
- fix ReadTheDocs build error -- AttributeError: module 'site' has no attribute 'getsitepackages'
- strip whitespace from append_sys_path and append_environ_path
- make pythonnet a required dependency only for Windows

Version 0.3.0 (2017.05.09)
==========================
*NOTE: This release breaks backward compatibility*

- can now pass \*\*kwargs from the Client64 constructor to the Server32-subclass constructor
- new command line arguments for starting the 32-bit server: --kwargs, --append_environ_path
- renamed the --append_path command line argument to --append_sys_path
- Server32.interactive_console() works on Windows and Linux
- edit documentation (thanks to @karna48 for the pull request)

Version 0.2.3 (2017.04.11)
==========================
- the frozen server32 executable (for Windows/Linux) now uses Python v3.6.1 and Python.NET v2.3.0
- include ctypes.util.find_library and sys.path when searching for shared library

Version 0.2.2 (2017.03.03)
==========================
- refreeze server32 executables

Version 0.2.1 (2017.03.02)
==========================
- fix releaselevel bug

Version 0.2.0 (2017.03.02)
==========================
- examples now working in Linux
- fix MSL namespace
- include all C# modules, classes and System.Type objects in the .NET loaded-library object
- create a custom C# library for the examples
- edit docstrings and documentation
- many bug fixes

Version 0.1.0 (2017.02.15)
==========================
- Initial release
