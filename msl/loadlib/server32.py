"""
Contains the base class for loading a 32-bit shared library in 32-bit Python.

The :class:`~.server32.Server32` class is used in combination with the
:class:`~.client64.Client64` class to communicate with a 32-bit shared library
from 64-bit Python.
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
from typing import Any

from .constants import IS_WINDOWS
from .constants import SERVER_FILENAME
from .load_library import LibTypes
from .load_library import LoadLibrary

METADATA: str = '-METADATA-'
SHUTDOWN: str = '-SHUTDOWN-'
OK: int = 200
ERROR: int = 500


class Server32(HTTPServer):

    def __init__(self,
                 path: str,
                 libtype: LibTypes,
                 host: str,
                 port: int,
                 **kwargs: Any) -> None:
        """Base class for loading a 32-bit library in 32-bit Python.

        All modules that are to be run on the 32-bit server must contain a class
        that is inherited from this class. The module may import most of the
        `standard <https://docs.python.org/3/py-modindex.html>`_ python modules.

        All modules that are run on the 32-bit server must be able to run on the Python
        interpreter that the server is running on, see :meth:`.version` for how to
        determine the version of the Python interpreter.

        :param path: The path to the 32-bit library (see :class:`.LoadLibrary`)
        :param libtype: The library type (see :class:`.LoadLibrary`).

            .. note::
               Since Java byte code is executed on the
               `JVM <https://en.wikipedia.org/wiki/Java_virtual_machine>`_
               it does not make sense to use :class:`Server32` for a Java
               ``.jar`` or ``.class`` file.

        :param host: The IP address (or hostname) to use for the server.
        :param port: The port to open for the server.
        :param kwargs: All keyword arguments are passed to :class:`.LoadLibrary`.
        """
        self._library = LoadLibrary(path, libtype=libtype, **kwargs)
        self._assembly = self._library.assembly
        self._lib = self._library.lib
        self._path = self._library.path
        super().__init__((host, int(port)), _RequestHandler, bind_and_activate=False)

    @property
    def assembly(self):
        """
        Returns a reference to the `.NET Runtime Assembly <NET_>`_ object if
        the shared library is .NET, otherwise returns :data:`None`.

        .. tip::
           The `JetBrains dotPeek`_ program can be used to reliably decompile any
           .NET Assembly into the equivalent source code.

        .. _NET: https://docs.microsoft.com/en-us/dotnet/api/system.reflection.assembly
        .. _JetBrains dotPeek: https://www.jetbrains.com/decompiler/
        """
        return self._assembly

    @property
    def lib(self):
        """Returns the reference to the library object.

        For example, if `libtype` is

            * `cdll` :math:`\\rightarrow` :class:`~ctypes.CDLL`
            * `windll` :math:`\\rightarrow` :class:`~ctypes.WinDLL`
            * `oledll` :math:`\\rightarrow` :class:`~ctypes.OleDLL`
            * `net` or `clr` :math:`\\rightarrow` :class:`~.load_library.DotNet`
            * `com` or `activex` :math:`\\rightarrow` :func:`POINTER <ctypes.POINTER>`
        """
        return self._lib

    @property
    def path(self) -> str:
        """The path to the shared library file."""
        return self._path

    @staticmethod
    def version() -> str:
        """Returns the version of Python that the 32-bit server is running on.

        .. invisible-code-block: pycon

           >>> SKIP_IF_MACOS()

        Example::

            >>> from msl.loadlib import Server32
            >>> Server32.version()
            'Python 3.11.4 ...'

        .. note::
            This method takes about 1 second to finish because the 32-bit server
            needs to start in order to determine the version of the Python interpreter.
        """
        exe = os.path.join(os.path.dirname(__file__), SERVER_FILENAME)
        return subprocess.check_output([exe, '--version']).decode().strip()

    @staticmethod
    def interactive_console() -> None:
        """Start an interactive console.

        This method starts an interactive console, in a new terminal, with the
        Python interpreter on the 32-bit server.

        Example::

            >>> from msl.loadlib import Server32  # doctest: +SKIP
            >>> Server32.interactive_console()  # doctest: +SKIP
        """
        exe = os.path.join(os.path.dirname(__file__), SERVER_FILENAME)
        if IS_WINDOWS:
            cmd = f'start "msl.loadlib.Server32 || interactive console" "{exe}" --interactive'
        else:
            cmd = f"gnome-terminal --command='{exe} --interactive'"
        os.system(cmd)

    @staticmethod
    def remove_site_packages_64bit() -> str:
        """Remove the site-packages directory from the 64-bit process.

        By default, the site-packages directory of the 64-bit process is
        included in :data:`sys.path` of the 32-bit process. Having the
        64-bit site-packages directory available can sometimes cause issues.
        For example, comtypes imports numpy so if numpy is installed in the
        64-bit process then comtypes will import the 64-bit version of numpy
        in the 32-bit process. Depending on the version of Python and/or numpy
        this can cause the 32-bit server to crash.

        .. versionadded:: 0.9

        Example::

            import sys
            from msl.loadlib import Server32

            class FileSystem(Server32):

                def __init__(self, host, port, **kwargs):

                    # remove the site-packages directory that was passed from 64-bit Python
                    # before calling the super() function to load the COM library
                    path = Server32.remove_site_packages_64bit()

                    super().__init__('Scripting.FileSystemObject', 'com', host, port)

                    # optional: add the site-packages directory back into sys.path
                    sys.path.append(path)

        :return: The path of the site-packages directory that was removed.
            Can be an empty string if the directory was not found in :data:`sys.path`.
        """
        for index, path in enumerate(sys.path):
            if path.endswith('site-packages'):
                return sys.path.pop(index)
        return ''

    @staticmethod
    def is_interpreter() -> bool:
        """Check if code is running on the 32-bit server.

        If the same module is executed by both
        :class:`~msl.loadlib.client64.Client64` and :class:`.Server32`
        then there may be only parts of the code that should only be executed
        by the correct bitness of the Python interpreter.

        .. versionadded:: 0.9

        Example::

            import sys
            from msl.loadlib import Server32

            if Server32.is_interpreter():
                # this only gets executed on the 32-bit server
                assert sys.maxsize < 2**32

        :return: Whether the code is running on the 32-bit server.
        """
        return sys.executable.endswith(SERVER_FILENAME)

    @staticmethod
    def examples_dir() -> str:
        """Get the directory where the example libraries are located.

        .. versionadded:: 0.9

        :return: The directory where the example libraries are located.
        """
        if Server32.is_interpreter():
            root = os.path.dirname(sys.executable)
        else:
            root = os.path.dirname(__file__)
        path = os.path.join(root, os.pardir, 'examples', 'loadlib')
        return os.path.abspath(path)

    def shutdown_handler(self) -> None:
        """Proxy function that is called immediately prior to the server shutting down.

        The intended use case is for the server to do any necessary cleanup, such as stopping
        locally started threads or closing file handles before it shuts down.

        .. versionadded:: 0.6
        """
        pass


class _RequestHandler(BaseHTTPRequestHandler):
    """Handles a request that was sent to the 32-bit server."""

    def do_GET(self):
        """Handle a GET request."""
        try:
            if self.path == METADATA:
                response = {
                    'path': self.server.path,
                    'pid': os.getpid(),
                    'unfrozen_dir': sys._MEIPASS,
                }
            else:
                with open(self.server.pickle_path, mode='rb') as f:
                    args = pickle.load(f)
                    kwargs = pickle.load(f)

                attr = getattr(self.server, self.path)
                if callable(attr):
                    response = attr(*args, **kwargs)
                else:
                    response = attr

            with open(self.server.pickle_path, mode='wb') as f:
                pickle.dump(response, f, protocol=self.server.pickle_protocol)

            self.send_response(OK)
            self.end_headers()

        except:  # noqa: PEP 8: E722 do not use bare 'except'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_list = traceback.extract_tb(exc_traceback)
            tb = tb_list[min(len(tb_list)-1, 1)]  # get the Server32 subclass exception
            response = {'name': exc_type.__name__, 'value': str(exc_value)}
            traceback_ = f'  File {tb[0]!r}, line {tb[1]}, in {tb[2]}'
            if tb[3]:
                traceback_ += f'\n    {tb[3]}'
            response['traceback'] = traceback_
            self.send_response(ERROR)
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """Handle a POST request."""
        if self.path == SHUTDOWN:
            self.server.shutdown_handler()
            threading.Thread(target=self.server.shutdown).start()
        else:  # the pickle info
            match = re.match(r'protocol=(\d+)&path=(.*)', self.path)
            if match:
                self.server.pickle_protocol = int(match.group(1))
                self.server.pickle_path = match.group(2)
                code = OK
            else:
                code = ERROR
            self.send_response(code)
            self.end_headers()

    def log_message(self, fmt: str, *args: Any) -> None:
        """
        Overrides: :meth:`~http.server.BaseHTTPRequestHandler.log_message`

        Ignore all log messages from being displayed in :data:`sys.stdout`.
        """
        pass
