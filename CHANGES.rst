=========
Changelog
=========

unreleased
==========
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
