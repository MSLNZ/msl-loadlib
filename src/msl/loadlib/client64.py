"""
Contains the base class for communicating with a 32-bit library from 64-bit Python.

The :class:`~.server32.Server32` class is used in combination with the
:class:`~.client64.Client64` class to communicate with a 32-bit shared library
from 64-bit Python.
"""

from __future__ import annotations

import importlib
import inspect
import io
import json
import os
import pickle
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import warnings
from http.client import CannotSendRequest
from http.client import HTTPConnection
from typing import Any
from typing import BinaryIO
from typing import Iterable
from typing import TypeVar

from . import utils
from .constants import IS_WINDOWS
from .constants import SERVER_FILENAME
from .exceptions import ConnectionTimeoutError
from .exceptions import ResponseTimeoutError
from .exceptions import Server32Error
from .load_library import PathLike
from .server32 import METADATA
from .server32 import OK
from .server32 import SHUTDOWN
from .server32 import Server32

# the Self type was added in Python 3.11 (PEP 673)
# using TypeVar is equivalent for < 3.11
Self = TypeVar("Self", bound="Client64")


class Client64:
    def __init__(
        self,
        module32: PathLike,
        *,
        add_dll_directory: PathLike | Iterable[PathLike] | None = None,
        append_environ_path: PathLike | Iterable[PathLike] | None = None,
        append_sys_path: PathLike | Iterable[PathLike] | None = None,
        host: str | None = "127.0.0.1",
        port: int | None = None,
        protocol: int = 5,
        rpc_timeout: float | None = None,
        server32_dir: PathLike | None = None,
        timeout: float = 10,
        **kwargs: Any,
    ) -> None:
        """Base class for communicating with a 32-bit library from 64-bit Python.

        Starts a 32-bit server, :class:`~.server32.Server32`, to host a Python class
        that is a wrapper around a 32-bit library. :class:`.Client64` runs within
        a 64-bit Python interpreter, and it sends a request to the server which calls
        the 32-bit library to execute the request. The server then provides a
        response back to the client.

        .. versionchanged:: 0.6
           Added the `rpc_timeout` argument.

        .. versionchanged:: 0.8
           Added the `protocol` argument and the default `quiet` value became :data:`None`.

        .. versionchanged:: 0.10
           Added the `server32_dir` argument.

        .. versionchanged:: 1.0
           Removed the deprecated `quiet` argument. The `host` value may now be `None`.
           Added the `add_dll_directory` argument.

        :param module32: The name of, or the path to, a Python module that will be
            imported by the 32-bit server. The module must contain a class that inherits
            from :class:`~.server32.Server32`.
        :param add_dll_directory: Add path(s) to the 32-bit server's DLL search path.
            See :func:`os.add_dll_directory` for more details. Available on Windows only.
        :param append_environ_path: Append path(s) to the 32-bit server's
            :data:`os.environ['PATH'] <os.environ>` variable. This may be useful if
            the library that is being loaded requires additional libraries that
            must be available on ``PATH``.
        :param append_sys_path: Append path(s) to the 32-bit server's :data:`sys.path`
            variable. The value of :data:`sys.path` from the 64-bit process is
            automatically included, i.e.,

            .. centered::
               ``sys.path(32bit) = sys.path(64bit) + append_sys_path``.
        :param host: The hostname (IP address) of the 32-bit server.
            If :data:`None` then the connection to the server is mocked.
            See :ref:`msl-loadlib-mock-connection` for more details.
        :param port: The port to open on the 32-bit server. If :data:`None`,
            an available port will be used.
        :param protocol: The :mod:`pickle` :ref:`protocol <pickle-protocols>` to use.
        :param rpc_timeout: The maximum number of seconds to wait for a response from the
            32-bit server. The `RPC <https://en.wikipedia.org/wiki/Remote_procedure_call>`_
            timeout value is used for *all* requests from the server. If you want different
            requests to have different timeout values, you will need to implement custom
            timeout handling for each method on the server. Default is :data:`None`, which
            means to use the default timeout value used by the :mod:`socket` module (which
            is to *wait forever*).
        :param server32_dir: The directory where the frozen 32-bit server is located.
        :param timeout: The maximum number of seconds to wait to establish a connection
            with the 32-bit server.
        :param kwargs: All additional keyword arguments are passed to the :class:`~.server32.Server32`
            subclass. The data type of each value is not preserved. It will be of type :class:`str`
            at the constructor of the :class:`~.server32.Server32` subclass.
        :raises OSError: If the 32-bit server cannot be found.
        :raises ConnectionTimeoutError: If the connection to the 32-bit server cannot be established.

        .. note::
            If `module32` is not located in the current working directory then you
            must either specify the full path to `module32` **or** you can
            specify the folder where `module32` is located by passing a value to the
            `append_sys_path` parameter. Using the `append_sys_path` option also allows
            for any other modules that `module32` may depend on to also be included
            in :data:`sys.path` so that those modules can be imported when `module32`
            is imported.
        """
        self._client: MockClient | HTTPClient | None = None
        if host is None:
            self._client = MockClient(
                os.fsdecode(module32),
                add_dll_directory=add_dll_directory,
                append_environ_path=append_environ_path,
                append_sys_path=append_sys_path,
                **kwargs,
            )
        else:
            self._client = HTTPClient(
                os.fsdecode(module32),
                add_dll_directory=add_dll_directory,
                append_environ_path=append_environ_path,
                append_sys_path=append_sys_path,
                host=host,
                port=port,
                protocol=protocol,
                rpc_timeout=rpc_timeout,
                server32_dir=server32_dir,
                timeout=timeout,
                **kwargs,
            )

    def __del__(self) -> None:
        try:
            self._client.cleanup()
        except AttributeError:
            pass

    def __enter__(self: Self) -> Self:
        return self

    def __exit__(self, *ignored) -> None:
        try:
            self._client.cleanup()
        except AttributeError:
            pass

    def __repr__(self) -> str:
        lib = os.path.basename(self._client.lib32_path)
        if self._client.host is None:
            return f"<{self.__class__.__name__} lib={lib} address=None (mocked)>"

        if self._client.connection is None:
            return f"<{self.__class__.__name__} lib={lib} address=None (closed)>"

        return f"<{self.__class__.__name__} lib={lib} address={self._client.host}:{self._client.port}>"

    @property
    def host(self) -> str | None:
        """The host address of the 32-bit server."""
        return self._client.host

    @property
    def port(self) -> int:
        """The port number of the 32-bit server."""
        return self._client.port

    @property
    def connection(self) -> HTTPConnection | None:
        """The connection to the 32-bit server."""
        return self._client.connection

    @property
    def lib32_path(self) -> str:
        """The path to the 32-bit shared-library file."""
        return self._client.lib32_path

    def request32(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Send a request to the 32-bit server.

        :param name: The name of a method, property or attribute of the :class:`~.server32.Server32` subclass.
        :param args: The arguments that the method in the :class:`~.server32.Server32` subclass requires.
        :param kwargs: The keyword arguments that the method in the :class:`~.server32.Server32` subclass requires.
        :return: Whatever is returned by calling `name`.
        :raises Server32Error: If there was an error processing the request on the 32-bit server.
        :raises ResponseTimeoutError: If a timeout occurs while waiting for the response from the 32-bit server.
        """
        return self._client.request32(name, *args, **kwargs)

    def shutdown_server32(self, kill_timeout: float = 10) -> tuple[BinaryIO, BinaryIO]:
        """Shutdown the 32-bit server.

        This method shuts down the 32-bit server, closes the client connection,
        and deletes the temporary file that is used to save the serialized
        :mod:`pickle`\'d data.

        .. versionchanged:: 0.6
           Added the `kill_timeout` argument.

        .. versionchanged:: 0.8
           Returns the (stdout, stderr) streams from the 32-bit server.

        :param kill_timeout: If the 32-bit server is still running after `kill_timeout`
            seconds, the server will be killed using brute force. A warning will be
            issued if the server is killed in this manner.
        :return: The (stdout, stderr) streams from the 32-bit server. Limit the total
            number of characters that are written to either stdout or stderr on
            the 32-bit server to be < 4096. This will avoid potential blocking
            when reading the stdout and stderr PIPE buffers.

        .. note::
            This method gets called automatically when the reference count to the
            :class:`.Client64` object reaches zero (see :meth:`~object.__del__`).
        """
        return self._client.shutdown_server32(kill_timeout=kill_timeout)


class HTTPClient:
    def __init__(
        self,
        module32: str,
        *,
        add_dll_directory: PathLike | Iterable[PathLike] | None = None,
        append_environ_path: PathLike | Iterable[PathLike] | None = None,
        append_sys_path: PathLike | Iterable[PathLike] | None = None,
        host: str | None = "127.0.0.1",
        port: int | None = None,
        protocol: int = 5,
        rpc_timeout: float | None = None,
        server32_dir: PathLike | None = None,
        timeout: float = 10,
        **kwargs: Any,
    ) -> None:
        """Start a server and connect to it."""
        self._meta32: dict[str, str | int] = {}
        self._conn: HTTPConnection | None = None
        self._proc: subprocess.Popen | None = None

        if port is None:
            port = utils.get_available_port()

        # the temporary files
        f = os.path.join(tempfile.gettempdir(), f"msl-loadlib-{host}-{port}")
        self._pickle_path = f"{f}.pickle"
        self._meta_path = f"{f}.txt"
        self._pickle_protocol = protocol

        # Find the 32-bit server executable.
        # Check a few locations in case msl-loadlib is frozen.
        dirs = [os.path.dirname(__file__)] if server32_dir is None else [os.fsdecode(server32_dir)]
        if getattr(sys, "frozen", False):
            # PyInstaller location for data files
            if hasattr(sys, "_MEIPASS"):
                dirs.append(sys._MEIPASS)

            # cx_Freeze location for data files
            dirs.append(os.path.dirname(sys.executable))

            # the current working directory
            dirs.append(os.getcwd())

        server_exe = None
        for d in dirs:
            f = os.path.join(d, SERVER_FILENAME)
            if os.path.isfile(f):
                server_exe = f
                break

        if server_exe is None:
            if len(dirs) == 1:
                msg = f"Cannot find {os.path.join(dirs[0], SERVER_FILENAME)}"
                raise OSError(msg)
            else:
                directories = "\n  ".join(sorted(set(dirs)))
                msg = f"Cannot find {SERVER_FILENAME!r} in any of the following directories:\n  {directories}"
                raise OSError(msg)

        cmd = [
            server_exe,
            "--module",
            module32,
            "--host",
            host,
            "--port",
            str(port),
        ]

        # include paths to the 32-bit server's sys.path
        sys_path = list(sys.path)
        sys_path.extend(_build_paths(append_sys_path, ignore=sys_path))
        cmd.extend(["--append-sys-path", ";".join(sys_path)])

        # include paths to the 32-bit server's os.environ['PATH']
        env_path = [os.getcwd()]
        env_path.extend(_build_paths(append_environ_path, ignore=env_path))
        cmd.extend(["--append-environ-path", ";".join(env_path)])

        # include paths to the 32-bit server's os.add_dll_directory()
        dll_dirs = _build_paths(add_dll_directory)
        if dll_dirs:
            cmd.extend(["--add-dll-directory", ";".join(dll_dirs)])

        # include any keyword arguments
        if kwargs:
            kw_str = ";".join(f"{k}={v}" for k, v in kwargs.items())
            cmd.extend(["--kwargs", kw_str])

        # start the 32-bit server
        flags = 0x08000000 if IS_WINDOWS else 0  # fixes issue 31, CREATE_NO_WINDOW = 0x08000000
        self._proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, creationflags=flags)
        try:
            utils.wait_for_server(host, port, timeout)
        except ConnectionTimeoutError as err:
            self._wait(timeout=0, stacklevel=5)
            # if the subprocess was killed then self._wait sets returncode to -2
            if self._proc.returncode == -2:
                self._cleanup_zombie_and_files()
                stdout = self._proc.stdout.read()
                if not stdout:
                    err.reason = (
                        f"If you add print() statements to {module32!r}\n"
                        f"the statements that are executed will be displayed here.\n"
                        f"Limit the total number of characters that are written to stdout to be < 4096\n"
                        f"to avoid potential blocking when reading the stdout PIPE buffer."
                    )
                else:
                    err.reason = f"stdout from {module32!r} is:\n{stdout.decode()}"
            else:
                err.reason = self._proc.stderr.read().decode(errors="ignore")
            raise

        # connect to the server
        self._rpc_timeout = socket.getdefaulttimeout() if rpc_timeout is None else rpc_timeout
        self._conn = HTTPConnection(host, port=port, timeout=self._rpc_timeout)
        self._host = self._conn.host
        self._port = self._conn.port

        # let the server know the info to use for pickling
        self._conn.request("POST", f"protocol={self._pickle_protocol}&path={self._pickle_path}")
        response = self._conn.getresponse()
        if response.status != OK:
            value = "Cannot set pickle info"
            raise Server32Error(value)

        self._meta32 = self.request32(METADATA)

    @property
    def host(self) -> str:
        """The host address of the 32-bit server."""
        return self._host

    @property
    def port(self) -> int:
        """The port number of the 32-bit server."""
        return self._port

    @property
    def connection(self) -> HTTPConnection:
        """The connection to the 32-bit server."""
        return self._conn

    @property
    def lib32_path(self) -> str:
        """The path to the 32-bit shared-library file."""
        return self._meta32["path"]

    def cleanup(self) -> None:
        """Shutdown the server and remove files."""
        try:
            out, err = self.shutdown_server32()
            out.close()
            err.close()
        except AttributeError:
            pass

        try:
            self._cleanup_zombie_and_files()
        except AttributeError:
            pass

    def request32(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Send a request to the 32-bit server."""
        if self._conn is None:
            value= "The connection to the 32-bit server is closed"
            raise Server32Error(value)

        with open(self._pickle_path, mode="wb") as f:
            pickle.dump(args, f, protocol=self._pickle_protocol)
            pickle.dump(kwargs, f, protocol=self._pickle_protocol)

        self._conn.request("GET", name)

        try:
            response = self._conn.getresponse()
        except socket.timeout:
            response = None

        if response is None:
            msg = f"Waiting for the response from the {name!r} request timed out after {self._rpc_timeout} second(s)"
            raise ResponseTimeoutError(msg)

        if response.status == OK:
            with open(self._pickle_path, mode="rb") as f:
                result = pickle.load(f)
            return result

        raise Server32Error(**json.loads(response.read().decode()))

    def shutdown_server32(self, kill_timeout: float = 10) -> tuple[BinaryIO, BinaryIO]:
        """Shutdown the 32-bit server."""
        if self._conn is None:
            return self._proc.stdout, self._proc.stderr  # noqa: stdout/stderr are not None

        # send the shutdown request
        try:
            self._conn.request("POST", SHUTDOWN)
        except CannotSendRequest:
            # can occur if the previous request raised ResponseTimeoutError
            # send the shutdown request again
            self._conn.close()
            self._conn = HTTPConnection(self.host, port=self.port)
            self._conn.request("POST", SHUTDOWN)

        # give the frozen 32-bit server a chance to shut down gracefully
        self._wait(timeout=kill_timeout, stacklevel=4)

        self._cleanup_zombie_and_files()

        self._conn.sock.shutdown(socket.SHUT_RDWR)
        self._conn.close()
        self._conn = None
        return self._proc.stdout, self._proc.stderr  # noqa: stdout/stderr are not None

    def _wait(self, timeout: float = 10, stacklevel: int = 4) -> None:
        # give the 32-bit server a chance to shut down gracefully
        t0 = time.time()
        while self._proc.poll() is None:
            try:
                time.sleep(0.1)
            except OSError:
                # could be raised while Python is shutting down
                #   OSError: [WinError 6] The handle is invalid
                pass

            if time.time() - t0 > timeout:
                self._proc.terminate()
                self._proc.returncode = -2
                warnings.warn("killed the 32-bit server using brute force", stacklevel=stacklevel)
                break

    def _cleanup_zombie_and_files(self) -> None:
        try:
            os.remove(self._pickle_path)
        except OSError:
            pass

        if self._meta32:
            pid = self._meta32["pid"]
            unfrozen_dir = self._meta32["unfrozen_dir"]
        else:
            try:
                with open(self._meta_path, mode="rt") as fp:
                    lines = fp.readlines()
            except (OSError, NameError):
                return
            else:
                pid, unfrozen_dir = int(lines[0]), lines[1]

        try:
            # the <signal.SIGKILL 9> constant is not available on Windows
            os.kill(pid, 9)
        except OSError:
            pass  # the server has already stopped

        # cleans up PyInstaller issue #2379 if the server was killed
        shutil.rmtree(unfrozen_dir, ignore_errors=True)

        try:
            os.remove(self._meta_path)
        except OSError:
            pass


class MockClient:
    def __init__(
        self,
        module32: str,
        *,
        add_dll_directory: PathLike | Iterable[PathLike] | None = None,
        append_environ_path: PathLike | Iterable[PathLike] | None = None,
        append_sys_path: PathLike | Iterable[PathLike] | None = None,
        **kwargs: Any,
    ) -> None:
        """Mocks the HTTP connection to the server."""
        self._added_dll_directories = []
        for path in _build_paths(add_dll_directory):
            self._added_dll_directories.append(os.add_dll_directory(path))

        if append_environ_path is not None:
            ignore = os.environ["PATH"].split(os.pathsep)
            new_env_paths = _build_paths(append_environ_path, ignore=ignore)
            if new_env_paths:
                os.environ["PATH"] += os.pathsep + os.pathsep.join(new_env_paths)

        # module32 may be a path to a Python file
        directory, module_name = os.path.split(module32)

        # must append specified paths to sys.path before importing module32
        if directory:
            if directory not in sys.path:
                sys.path.append(directory)
        if append_sys_path is not None:
            sys.path.extend(_build_paths(append_sys_path, ignore=sys.path))

        # get the Server32 subclass in the module
        cls = None
        if module_name.endswith(".py"):
            mod = importlib.import_module(module_name[:-3])
        else:
            mod = importlib.import_module(module_name)
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            if name != "Server32" and issubclass(obj, Server32):
                cls = obj
                break

        if cls is None:
            msg = f"Module {module32!r} does not contain a class that is a subclass of Server32"
            raise AttributeError(msg)

        # the Server32 subclass expects the values for all kwargs
        # to be of type string
        kw = dict((key, str(value)) for key, value in kwargs.items())

        self.server = cls(None, -1, **kw)  # noqa: (host, port, **kwargs)

    def cleanup(self) -> None:
        """Close the socket (which was never bound and activated)."""
        self.server.socket.close()

        for directory in self._added_dll_directories:
            if directory.path:
                directory.close()
        self._added_dll_directories.clear()

    @property
    def connection(self) -> None:
        """The connection to the mocked server."""
        return

    @property
    def host(self) -> None:
        """The host address of the mocked server."""
        return

    @property
    def lib32_path(self) -> str:
        """The path to the shared-library file."""
        return self.server.path

    @property
    def port(self) -> int:
        """The port number of the mocked server."""
        return -1

    def request32(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Send a request to the mocked server."""
        try:
            attr = getattr(self.server, name)
            if callable(attr):
                return attr(*args, **kwargs)
            else:
                return attr
        except Exception as exc:  # noqa: Too broad exception clause
            exception = {
                "name": exc.__class__.__name__,
                "value": f"The mocked connection to the server raised:\n{exc}\n(see above for more details)",
            }
            raise Server32Error(**exception) from exc

    def shutdown_server32(self, **ignored) -> tuple[BinaryIO, BinaryIO]:
        """Shutdown the mocked server."""
        self.cleanup()
        return io.BytesIO(), io.BytesIO()


def _build_paths(paths: PathLike | Iterable[PathLike] | None, *, ignore: list[str] = None) -> list[str]:
    """Build a list of absolute paths."""
    if paths is None:
        return []

    if ignore is None:
        ignore = []

    if isinstance(paths, (str, bytes, os.PathLike)):
        paths = [paths]

    out = []
    for p in paths:
        path = os.path.abspath(os.fsdecode(p))
        if path not in ignore:
            out.append(path)
    return out
