"""
Contains the base class for communicating with a 32-bit library from 64-bit Python.

The :class:`~.server32.Server32` class is used in combination with the
:class:`~.client64.Client64` class to communicate with a 32-bit shared library
from 64-bit Python.
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import warnings
try:
    from http.client import CannotSendRequest
    from http.client import HTTPConnection
    import pickle
except ImportError:  # then Python 2
    from httplib import CannotSendRequest
    from httplib import HTTPConnection
    import cPickle as pickle

from . import IS_PYTHON2
from . import IS_WINDOWS
from . import SERVER_FILENAME
from . import utils
from .exceptions import ConnectionTimeoutError
from .exceptions import ResponseTimeoutError
from .exceptions import Server32Error
from .server32 import METADATA
from .server32 import OK
from .server32 import SHUTDOWN

_encoding = sys.getfilesystemencoding()


class Client64(object):

    def __init__(self, module32, host='127.0.0.1', port=None, timeout=10.0,
                 quiet=None, append_sys_path=None, append_environ_path=None,
                 rpc_timeout=None, protocol=None, server32_dir=None, **kwargs):
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

        Parameters
        ----------
        module32 : :class:`str`
            The name of the Python module that is to be imported by the 32-bit server.
        host : :class:`str`, optional
            The address of the 32-bit server. Default is ``'127.0.0.1'``.
        port : :class:`int`, optional
            The port to open on the 32-bit server. Default is :data:`None`, which means
            to automatically find a port that is available.
        timeout : :class:`float`, optional
            The maximum number of seconds to wait to establish a connection to the
            32-bit server. Default is 10 seconds.
        quiet : :class:`bool`, optional
            This keyword argument is no longer used and will be removed in a future release.
        append_sys_path : :class:`str` or :class:`list` of :class:`str`, optional
            Append path(s) to the 32-bit server's :data:`sys.path` variable. The value of
            :data:`sys.path` from the 64-bit process is automatically included,
            i.e., ``sys.path(32bit) = sys.path(64bit) + append_sys_path``.
        append_environ_path : :class:`str` or :class:`list` of :class:`str`, optional
            Append path(s) to the 32-bit server's :data:`os.environ['PATH'] <os.environ>`
            variable. This can be useful if the library that is being loaded requires
            additional libraries that must be available on ``PATH``.
        rpc_timeout : :class:`float`, optional
            The maximum number of seconds to wait for a response from the 32-bit server.
            The `RPC <https://en.wikipedia.org/wiki/Remote_procedure_call>`_ timeout value
            is used for *all* requests from the server. If you want different requests to
            have different timeout values then you will need to implement custom timeout
            handling for each method on the server. Default is :data:`None`, which means
            to use the default timeout value used by the :mod:`socket` module (which is
            to *wait forever*).
        protocol : :class:`int`, optional
            The :mod:`pickle` :ref:`protocol <pickle-protocols>` to use. If not
            specified then determines the value to use based on the version of
            Python that the :class:`.Client64` is running in.
        server32_dir : :class:`str`, optional
            The directory where the frozen 32-bit server is located.
        **kwargs
            All additional keyword arguments are passed to the :class:`~.server32.Server32`
            subclass. The data type of each value is not preserved. It will be a string
            at the constructor of the :class:`~.server32.Server32` subclass.

        Note
        ----
        If `module32` is not located in the current working directory then you
        must either specify the full path to `module32` **or** you can
        specify the folder where `module32` is located by passing a value to the
        `append_sys_path` parameter. Using the `append_sys_path` option also allows
        for any other modules that `module32` may depend on to also be included
        in :data:`sys.path` so that those modules can be imported when `module32`
        is imported.

        Raises
        ------
        ~msl.loadlib.exceptions.ConnectionTimeoutError
            If the connection to the 32-bit server cannot be established.
        OSError
            If the frozen executable cannot be found.
        TypeError
            If the data type of `append_sys_path` or `append_environ_path` is invalid.
        """
        self._meta32 = {}
        self._conn = None
        self._proc = None

        if port is None:
            port = utils.get_available_port()

        # the temporary files
        f = os.path.join(tempfile.gettempdir(), 'msl-loadlib-{}-{}'.format(host, port))
        self._pickle_path = f + '.pickle'
        self._meta_path = f + '.txt'

        if protocol is None:
            # select the pickle protocol to use based on the 64-bit version of Python
            major, minor = sys.version_info[:2]
            if major == 2:
                self._pickle_protocol = 2
            elif major == 3 and minor < 4:
                self._pickle_protocol = 3
            elif major == 3 and minor < 8:
                self._pickle_protocol = 4
            else:
                self._pickle_protocol = 5
        else:
            self._pickle_protocol = protocol

        # Find the 32-bit server executable.
        # Check a few locations in case msl-loadlib is frozen.
        dirs = [os.path.dirname(__file__)] if server32_dir is None else [server32_dir]
        if getattr(sys, 'frozen', False):
            # PyInstaller location for data files
            if hasattr(sys, '_MEIPASS'):
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
                raise OSError('Cannot find ' + os.path.join(dirs[0], SERVER_FILENAME))
            else:
                directories = '\n  '.join(sorted(set(dirs)))
                raise OSError('Cannot find {!r} in any of the following directories:'
                              '\n  {}'.format(SERVER_FILENAME, directories))

        cmd = [
            server_exe,
            '--module', module32,
            '--host', host,
            '--port', str(port)
        ]

        # include paths to the 32-bit server's sys.path
        sys_path = list(sys.path)
        if append_sys_path is not None:
            if isinstance(append_sys_path, str) or (IS_PYTHON2 and isinstance(append_sys_path, unicode)):
                sys_path.append(append_sys_path)
            elif isinstance(append_sys_path, (list, tuple)):
                sys_path.extend(append_sys_path)
            else:
                raise TypeError('append_sys_path must be a str, list or tuple')
        if IS_PYTHON2:
            sys_path = [p.encode(_encoding) if isinstance(p, unicode) else p for p in sys_path]
        cmd.extend(['--append-sys-path', ';'.join(sys_path)])  # don't replace ';' with os.pathsep

        # include paths to the 32-bit server's os.environ['PATH']
        env_path = [os.getcwd()]
        if append_environ_path is not None:
            if isinstance(append_environ_path, str) or (IS_PYTHON2 and isinstance(append_sys_path, unicode)):
                env_path.append(append_environ_path)
            elif isinstance(append_environ_path, (list, tuple)):
                env_path.extend(append_environ_path)
            else:
                raise TypeError('append_environ_path must be a str, list or tuple')
        if IS_PYTHON2:
            env_path = [p.encode(_encoding) if isinstance(p, unicode) else p for p in env_path]
        cmd.extend(['--append-environ-path', ';'.join(env_path)])  # don't replace ';' with os.pathsep

        # include any keyword arguments
        if kwargs:
            kw_str = ';'.join('{}={}'.format(key, value) for key, value in kwargs.items())
            cmd.extend(['--kwargs', kw_str])

        # TODO the `quiet` kwarg is deprecated
        if quiet is not None:
            warnings.simplefilter('once', DeprecationWarning)
            warnings.warn(
                "the 'quiet' keyword argument for Client64 is ignored and will be removed in a future release",
                DeprecationWarning,
                stacklevel=2
            )

        # start the 32-bit server
        flags = 0x08000000 if IS_WINDOWS else 0  # fixes issue 31, CREATE_NO_WINDOW = 0x08000000
        self._proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, creationflags=flags)
        try:
            utils.wait_for_server(host, port, timeout)
        except ConnectionTimeoutError as err:
            self._wait(timeout=0, stacklevel=4)
            # if the subprocess was killed then self._wait sets returncode to -2
            if self._proc.returncode == -2:
                self._cleanup_zombie_and_files()
                stdout = self._proc.stdout.read()
                if not stdout:
                    err.reason = 'If you add print() statements to {!r}\n' \
                                 'the statements that are executed will be displayed here.\n' \
                                 'Limit the total number of characters that are written to stdout to be < 4096\n' \
                                 'to avoid potential blocking when reading the stdout PIPE buffer.'.format(module32)
                else:
                    decoded = stdout.decode(encoding='utf-8', errors='replace')
                    err.reason = 'stdout from {!r} is:\n{}'.format(module32, decoded)
            else:
                stderr = self._proc.stderr.read()
                err.reason = stderr.decode(encoding='utf-8', errors='replace')
            raise

        # connect to the server
        self._rpc_timeout = socket.getdefaulttimeout() if rpc_timeout is None else rpc_timeout
        self._conn = HTTPConnection(host, port=port, timeout=self._rpc_timeout)

        # let the server know the info to use for pickling
        self._conn.request('POST', 'protocol={}&path={}'.format(self._pickle_protocol, self._pickle_path))
        response = self._conn.getresponse()
        if response.status != OK:
            raise Server32Error('Cannot set pickle info')

        self._meta32 = self.request32(METADATA)

    def __del__(self):
        try:
            self._cleanup()
        except:
            pass

    def __repr__(self):
        msg = '<{} '.format(self.__class__.__name__)
        if self._conn:
            lib = os.path.basename(self._meta32['path'])
            return msg + 'lib={} address={}:{}>'.format(lib, self._conn.host, self._conn.port)
        else:
            return msg + 'lib=None address=None>'

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self._cleanup()

    @property
    def host(self):
        """:class:`str`: The address of the host for the :attr:`~msl.loadlib.client64.Client64.connection`."""
        return self._conn.host

    @property
    def port(self):
        """:class:`int`: The port number of the :attr:`~msl.loadlib.client64.Client64.connection`."""
        return self._conn.port

    @property
    def connection(self):
        """:class:`~http.client.HTTPConnection`: The reference to the connection to the 32-bit server."""
        return self._conn

    @property
    def lib32_path(self):
        """The path to the 32-bit library.

        Returns
        -------
        :class:`str`
            The path to the 32-bit shared-library file.
        """
        return self._meta32['path']

    def request32(self, name, *args, **kwargs):
        """Send a request to the 32-bit server.

        Parameters
        ----------
        name : :class:`str`
            The name of an attribute of the :class:`~.server32.Server32` subclass.
            The name can be a method, property or any attribute.
        *args
            The arguments that the method in the :class:`~.server32.Server32` subclass requires.
        **kwargs
            The keyword arguments that the method in the :class:`~.server32.Server32` subclass requires.

        Returns
        -------
        Whatever is returned by the method of the :class:`~.server32.Server32` subclass.

        Raises
        ------
        ~msl.loadlib.exceptions.Server32Error
            If there was an error processing the request on the 32-bit server.
        ~msl.loadlib.exceptions.ResponseTimeoutError
            If a timeout occurs while waiting for the response from the 32-bit server.
        """
        if self._conn is None:
            raise Server32Error('The 32-bit server is not active')

        with open(self._pickle_path, mode='wb') as f:
            pickle.dump(args, f, protocol=self._pickle_protocol)
            pickle.dump(kwargs, f, protocol=self._pickle_protocol)

        self._conn.request('GET', name)

        try:
            response = self._conn.getresponse()
        except socket.timeout:
            response = None

        if response is None:
            raise ResponseTimeoutError(
                'Waiting for the response from the {!r} request timed '
                'out after {} seconds'.format(name, self._rpc_timeout)
            )

        if response.status == OK:
            with open(self._pickle_path, mode='rb') as f:
                result = pickle.load(f)
            return result

        raise Server32Error(**json.loads(response.read().decode(encoding='utf-8', errors='replace')))

    def shutdown_server32(self, kill_timeout=10):
        """Shutdown the 32-bit server.

        This method shuts down the 32-bit server, closes the client connection,
        and deletes the temporary file that is used to save the serialized
        :mod:`pickle`\'d data.

        .. versionchanged:: 0.6
           Added the `kill_timeout` argument.

        .. versionchanged:: 0.8
           Returns the (stdout, stderr) streams from the 32-bit server.

        Parameters
        ----------
        kill_timeout : :class:`float`, optional
            If the 32-bit server is still running after `kill_timeout` seconds then
            the server will be killed using brute force. A warning will be issued
            if the server is killed in this manner.

        Returns
        -------
        :class:`tuple`
            The (stdout, stderr) streams from the 32-bit server. Limit the total
            number of characters that are written to either stdout or stderr on
            the 32-bit server to be < 4096. This will avoid potential blocking
            when reading the stdout and stderr PIPE buffers.

        Note
        ----
        This method gets called automatically when the reference count to the
        :class:`~.client64.Client64` object reaches 0 -- see :meth:`~object.__del__`.
        """
        if self._conn is None:
            return self._proc.stdout, self._proc.stderr

        # send the shutdown request
        try:
            self._conn.request('POST', SHUTDOWN)
        except CannotSendRequest:
            # can occur if the previous request raised ResponseTimeoutError
            # send the shutdown request again
            self._conn.close()
            self._conn = HTTPConnection(self.host, port=self.port)
            self._conn.request('POST', SHUTDOWN)

        # give the frozen 32-bit server a chance to shut down gracefully
        self._wait(timeout=kill_timeout, stacklevel=3)

        self._cleanup_zombie_and_files()

        self._conn.sock.shutdown(socket.SHUT_RDWR)
        self._conn.close()
        self._conn = None
        return self._proc.stdout, self._proc.stderr

    def _wait(self, timeout=10., stacklevel=3):
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
                warnings.warn('killed the 32-bit server using brute force', stacklevel=stacklevel)
                break

    def _cleanup(self):
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

    def _cleanup_zombie_and_files(self):
        try:
            os.remove(self._pickle_path)
        except OSError:
            pass

        if self._meta32:
            pid = self._meta32['pid']
            unfrozen_dir = self._meta32['unfrozen_dir']
        else:
            try:
                with open(self._meta_path, mode='rt') as fp:
                    lines = fp.readlines()
            except (IOError, OSError, NameError):
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
