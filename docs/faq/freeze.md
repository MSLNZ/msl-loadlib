# Freezing the `msl-loadlib` package {: #faq-freeze }

If you want to use [PyInstaller]{:target="_blank"} or [cx-Freeze]{:target="_blank"} to bundle `msl-loadlib` in a frozen application, the 32-bit server must be added as a data file.

For example, using [PyInstaller]{:target="_blank"} on Windows you would include an ``--add-data`` option

```console
pyinstaller --add-data "..\site-packages\msl\loadlib\server32-windows.exe:."
```

where you must replace the leading `..` prefix with the parent directories to the file (i.e., specify the absolute path to the file). On Linux, replace `server32-windows.exe:.` with `server32-linux:.`

If the server is loading a .NET library that was compiled with .NET &lt; 4.0, you must also add the `server32-windows.exe.config` data file. Otherwise, you do not need to add this config file.

[cx-Freeze]{:target="_blank"} appears to automatically bundle the 32-bit server (tested with [cx-Freeze]{:target="_blank"} version 6.14.5) so there may not be anything you need to do. If the `server32` executable is not bundled, you can specify the absolute path to the `server32` executable as the `include_files` option for the `build_exe` command.

You may also wish to [refreeze][] the 32-bit server and add your custom server to your application.

[PyInstaller]: https://pyinstaller.org/en/stable/
[cx-Freeze]: https://cx-freeze.readthedocs.io/en/latest/index.html
