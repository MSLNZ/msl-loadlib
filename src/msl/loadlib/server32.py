"""Base class for loading a 32-bit library in 32-bit Python.

[Server32][] is used in combination with [Client64][] to communicate with
a 32-bit library from 64-bit Python.
"""

from __future__ import annotations

import json
import os
import pickle
import re
import subprocess
import sys
import threading
import traceback
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from typing import Any, TYPE_CHECKING

from .constants import IS_WINDOWS
from .constants import SERVER_FILENAME
from .load_library import LibType
from .load_library import LoadLibrary

if TYPE_CHECKING:
    from msl.loadlib.activex import Application

METADATA: str = "-METADATA-"
SHUTDOWN: str = "-SHUTDOWN-"
OK: int = 200
ERROR: int = 500


class Server32(HTTPServer):
    """Base class for loading a 32-bit library in 32-bit Python."""

    def __init__(self, path: str, libtype: LibType, host: str, port: int, **kwargs: Any) -> None:
        """Base class for loading a 32-bit library in 32-bit Python.

        All modules that are to be run on the 32-bit server must contain a class
        that inherits this class. The module may import most of the
        [standard](https://docs.python.org/3/py-modindex.html){:target="_blank"}
        python modules (graphic-related modules, e.g., [tkinter][]{:target="_blank"},
        are not available).

        Args:
            path: The path to the 32-bit library (see [LoadLibrary][msl.loadlib.load_library.LoadLibrary])
            libtype: The library type (see [LoadLibrary][msl.loadlib.load_library.LoadLibrary]).

                !!! attention
                    Since Java byte code is executed on the
                    [JVM](https://en.wikipedia.org/wiki/Java_virtual_machine){:target="_blank"}
                    it does not make sense to use [Server32][] for a Java `.jar` or `.class` file.
                    Use [LoadLibrary][msl.loadlib.load_library.LoadLibrary] to load a Java library.

            host: The IP address (or hostname) to use for the server.
            port: The port to open for the server.
            kwargs: All keyword arguments are passed to [LoadLibrary][msl.loadlib.load_library.LoadLibrary].
        """
        self._library = LoadLibrary(path, libtype=libtype, **kwargs)
        self._app = self._library.application
        self._assembly = self._library.assembly
        self._lib = self._library.lib
        self._path = self._library.path
        super().__init__((host, int(port)), _RequestHandler, bind_and_activate=False)

    @property
    def application(self) -> Application | None:
        """[Application][msl.loadlib.activex.Application] | `None` &mdash; Reference to the ActiveX application window.

        If the loaded library is not an ActiveX library, returns `None`.

        When an ActiveX library is loaded, the window is not shown
        (to show it call [Application.show][msl.loadlib.activex.Application.show])
        and the message loop is not running
        (to run it call [Application.run][msl.loadlib.activex.Application.run]).

        !!! note "Added in version 1.0"
        """
        return self._app

    @property
    def assembly(self) -> Any:
        """Returns a reference to the [.NET Runtime Assembly]{:target="_blank"} object.

        If the loaded library is not a .NET library, returns `None`.

        !!! tip
            The [JetBrains dotPeek]{:target="_blank"} program can be used to decompile a .NET Assembly.

        [.NET Runtime Assembly]: https://docs.microsoft.com/en-us/dotnet/api/system.reflection.assembly
        [JetBrains dotPeek]: https://www.jetbrains.com/decompiler/
        """
        return self._assembly

    @property
    def lib(self) -> Any:
        """Returns the reference to the library object.

        For example, if `libtype` is

        * `cdll` &#8594; [ctypes.CDLL][]{:target="_blank"}
        * `windll` &#8594; [ctypes.WinDLL][]{:target="_blank"}
        * `oledll` &#8594; [ctypes.OleDLL][]{:target="_blank"}
        * `net` or `clr` &#8594; An object containing .NET [namespace]{:target="_blank"}s,
            classes and [System.Type]{:target="_blank"}s
        * `com` or `activex` &#8594; [ctypes.POINTER][]{:target="_blank"}

        [namespace]: https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/namespace
        [System.Type]: https://learn.microsoft.com/en-us/dotnet/api/system.type
        """
        return self._lib

    @property
    def path(self) -> str:
        """[str][] &mdash; The path to the library file."""
        return self._path

    @staticmethod
    def version() -> str:
        """[str][] &mdash; The version of Python that the 32-bit server is running on.

        !!! tip
            You can get the version from a terminal by running
            ```console
            python -c "from msl.loadlib import Server32; Server32.version()"
            ```
        """
        exe = os.path.join(os.path.dirname(__file__), SERVER_FILENAME)
        return subprocess.check_output([exe, "--version"]).decode().strip()

    @staticmethod
    def interactive_console() -> None:
        """Start an [interactive console]{:target="_blank"}.

        This method starts an [interactive console]{:target="_blank"}, in a new terminal,
        with the Python interpreter on the 32-bit server.

        !!! tip
            You can start the console from a terminal by running
            ```console
            python -c "from msl.loadlib import Server32; Server32.interactive_console()"
            ```

        [interactive console]: https://docs.python.org/3/tutorial/interpreter.html#interactive-mode
        """
        exe = os.path.join(os.path.dirname(__file__), SERVER_FILENAME)
        if IS_WINDOWS:
            cmd = f'start "msl.loadlib.Server32 || interactive console" "{exe}" --interactive'
        else:
            cmd = f"gnome-terminal --command='{exe} --interactive'"
        os.system(cmd)

    @staticmethod
    def remove_site_packages_64bit() -> str:
        """Remove the _site-packages_ directory from the 64-bit process.

        By default, the _site-packages_ directory of the 64-bit process is
        included in [sys.path][] of the 32-bit process. Having the
        64-bit _site-packages_ directory available can sometimes cause issues.
        For example, `comtypes` tries to import `numpy` so if `numpy` is
        installed in the 64-bit process then `comtypes` will import the
        64-bit version of `numpy` in the 32-bit process. Depending on the
        version of Python and/or `numpy` this can cause the 32-bit server
        to crash.

        **Example:**

        ```python
        import sys
        from msl.loadlib import Server32

        class FileSystem(Server32):

            def __init__(self, host, port):

                # Remove the site-packages directory that was passed from 64-bit Python
                path = Server32.remove_site_packages_64bit()

                # Load the COM library (this is when `comtypes` gets imported)
                super().__init__("Scripting.FileSystemObject", "com", host, port)

                # Optional: add the site-packages directory back into sys.path
                sys.path.append(path)
        ```

        Returns:
            The path to the _site-packages_ directory that was removed.
                Can be an empty string if the directory was not found in [sys.path][].

        !!! note "Added in version 0.9"
        """
        for index, path in enumerate(sys.path):
            if path.endswith("site-packages"):
                return sys.path.pop(index)
        return ""

    @staticmethod
    def is_interpreter() -> bool:
        """Check if code is running on the 32-bit server.

        If the same module is executed by both [Client64][] and [Server32][]
        then there may be sections of the code that should only be executed
        by the correct bitness of the Python interpreter.

        **Example:**

        ```python
        import sys
        from msl.loadlib import Client64, Server32

        if Server32.is_interpreter():
            # Only executed on the 32-bit server
            assert sys.maxsize < 2**32
        ```

        Returns:
            Whether the module is running on the 32-bit server.

        !!! note "Added in version 0.9"
        """
        return sys.executable.endswith(SERVER_FILENAME)

    @staticmethod
    def examples_dir() -> str:
        """[str][] &mdash; The directory where the [example][direct] libraries are located.

        !!! note "Added in version 0.9"
        """
        if Server32.is_interpreter():
            root = os.path.dirname(sys.executable)
        else:
            root = os.path.dirname(__file__)
        path = os.path.join(root, os.pardir, "examples", "loadlib")
        return os.path.abspath(path)

    def shutdown_handler(self) -> None:
        """Called just before the server shuts down.

        Override this method to do any necessary cleanup, such as stopping
        threads or closing file handles, before the server shuts down.

        !!! note "Added in version 0.6"
        """


class _RequestHandler(BaseHTTPRequestHandler):
    """Handles a request that was sent to the 32-bit server."""

    def do_GET(self):
        """Handle a GET request."""
        try:
            if self.path == METADATA:
                response = {
                    "path": self.server.path,
                    "pid": os.getpid(),
                    "unfrozen_dir": sys._MEIPASS,
                }
            else:
                with open(self.server.pickle_path, mode="rb") as f:
                    args = pickle.load(f)
                    kwargs = pickle.load(f)

                attr = getattr(self.server, self.path)
                if callable(attr):
                    response = attr(*args, **kwargs)
                else:
                    response = attr

            with open(self.server.pickle_path, mode="wb") as f:
                pickle.dump(response, f, protocol=self.server.pickle_protocol)

            self.send_response(OK)
            self.end_headers()

        except:  # noqa: PEP 8: E722 do not use bare 'except'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_list = traceback.extract_tb(exc_traceback)
            tb = tb_list[min(len(tb_list) - 1, 1)]  # get the Server32 subclass exception
            response = {"name": exc_type.__name__, "value": str(exc_value)}
            traceback_ = f"  File {tb[0]!r}, line {tb[1]}, in {tb[2]}"
            if tb[3]:
                traceback_ += f"\n    {tb[3]}"
            response["traceback"] = traceback_
            self.send_response(ERROR)
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """Handle a POST request."""
        if self.path == SHUTDOWN:
            self.server.shutdown_handler()
            threading.Thread(target=self.server.shutdown).start()
        else:  # the pickle info
            match = re.match(r"protocol=(\d+)&path=(.*)", self.path)
            if match:
                self.server.pickle_protocol = int(match.group(1))
                self.server.pickle_path = match.group(2)
                code = OK
            else:
                code = ERROR
            self.send_response(code)
            self.end_headers()

    def log_message(self, fmt: str, *args: Any) -> None:
        """Overrides: http.server.BaseHTTPRequestHandler.log_message.

        Ignore all log messages from being displayed in `sys.stdout`.
        """
