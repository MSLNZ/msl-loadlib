# Custom Server {: #refreeze }

If you want to create a custom 32-bit server, you will need

* a 32-bit version of Python (version 3.8 or later) installed
* [PyInstaller]{:target="_blank"} installed in the 32-bit Python environment (ideally, you would use a [virtual environment][venv]{:target="_blank"} to install the necessary packages to create the server)

Some reasons why you may want to create a custom 32-bit server are that you want to

* run the server with a different version of Python,
* build the server for a different architecture,
* install a different version of `comtypes` or `pythonnet` (on Windows),
* install additional packages on the server (e.g., `numpy`, `my_custom_package`),
* embed your own data files in the frozen server.

Using pip from a 32-bit Python interpreter, run

!!! note "You may also want to install additional packages."

```console
pip install msl-loadlib pyinstaller
```

You have two options to create a 32-bit server

1. [Using the API][refreeze-api]
2. [Using the CLI][refreeze-cli]

and you have two options to use your custom server

1. Copy your `server32-*` file to the `../site-packages/msl/loadlib` directory where you have `msl-loadlib` installed in your 64-bit version of Python to replace the existing server file.
2. Specify the directory where your `server32-*` file is located as the value of the `server32_dir` keyword argument in [Client64][].

## Using the API {: #refreeze-api }

Create a script that calls the [freeze_server32.main][msl.loadlib.freeze_server32.main] function with the appropriate keyword arguments and run your script using a 32-bit Python interpreter. For example, the following script will include 32-bit `numpy` on the server

```python
from msl.loadlib import freeze_server32
freeze_server32.main(imports="numpy")
```

## Using the CLI {: #refreeze-cli }

When `msl-loadlib` is installed, a console script is included (named `freeze32`) that may be executed from the command line to create a new frozen 32-bit server.

To see the help for `freeze32`, run

```console
freeze32 --help
```

For example, if you want to include your own package and data files, you would run

```console
freeze32 --imports my_package --data .\my_data\lib32.dll
```

[PyInstaller]: https://www.pyinstaller.org/
