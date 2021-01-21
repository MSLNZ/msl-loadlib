"""
Contains the base class for communicating with a 32-bit library from 64-bit Python.

The :class:`~.server32.Server32` class is used in combination with the
:class:`~.client64.Client64` class to communicate with a 32-bit shared library
from 64-bit Python.
"""
import os
import sys
import uuid
import json
import time
import socket
import tempfile
import warnings
import subprocess
try:
    from http.client import HTTPConnection, CannotSendRequest
    import pickle
except ImportError:  # then Python 2
    import cPickle as pickle
    from httplib import HTTPConnection, CannotSendRequest

from . import (
    utils,
    SERVER_FILENAME,
    IS_PYTHON2
)
from .server32 import (
    METADATA,
    SHUTDOWN,
    OK,
)
from .exceptions import (
    Server32Error,
    ConnectionTimeoutError,
    ResponseTimeoutError
)

_encoding = sys.getfilesystemencoding()


class Client64(object):

    def __init__(self, module32, host='127.0.0.1', port=None, timeout=10.0,
                 quiet=None, append_sys_path=None, append_environ_path=None,
                 rpc_timeout=None, protocol=None, **kwargs):
        """Base class for communicating with a 32-bit library from 64-bit Python.

        Starts a 32-bit server, :class:`~.server32.Server32`, to host a Python class
        that is a wrapper around a 32-bit library. :class:`.Client64` runs within
        a 64-bit Python interpreter and it sends a request to the server which calls
        the 32-bit library to execute the request. The server then provides a
        response back to the client.

        .. versionchanged:: 0.6
           Added the `rpc_timeout` argument.

        .. versionchanged:: 0.8
           Added the `protocol` argument and the default `quiet` value became :data:`None`.

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
        IOError
            If the frozen executable cannot be found.
        TypeError
            If the data type of `append_sys_path` or `append_environ_path` is invalid.
        """
        self._meta32 = None
        self._conn = None

        if port is None:
            port = utils.get_available_port()

        # the temporary file to use to save the pickle'd data
        self._pickle_path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4())+'.pickle')

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
                # TODO protocol version 5 was added in Python 3.8 (see PEP 574).
                self._pickle_protocol = 4
        else:
            self._pickle_protocol = protocol

        # make sure that the server32 executable exists
        server_exe = os.path.join(os.path.dirname(__file__), SERVER_FILENAME)
        if not os.path.isfile(server_exe):
            raise IOError('Cannot find ' + server_exe)

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
                'the `quiet` keyword argument for Client64 is ignored and will be removed in version 0.9',
                DeprecationWarning,
                stacklevel=2
            )

        # start the 32-bit server
        self._proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        try:
            utils.wait_for_server(host, port, timeout)
        except ConnectionTimeoutError as err:
            self._proc.wait()
            err.reason = self._proc.stderr.read().decode(encoding='utf-8', errors='replace')
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

    def __repr__(self):
        msg = '<{} '.format(self.__class__.__name__)
        if self._conn:
            lib = os.path.basename(self._meta32['path'])
            return msg + 'lib={} address={}:{}>'.format(lib, self._conn.host, self._conn.port)
        else:
            return msg + 'lib=None address=None>'

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

    def request32(self, method32, *args, **kwargs):
        """Send a request to the 32-bit server.

        Parameters
        ----------
        method32 : :class:`str`
            The name of the method to call in the :class:`~.server32.Server32` subclass.
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

        with open(self._pickle_path, 'wb') as f:
            pickle.dump(args, f, protocol=self._pickle_protocol)
            pickle.dump(kwargs, f, protocol=self._pickle_protocol)

        self._conn.request('GET', method32)

        try:
            response = self._conn.getresponse()
        except socket.timeout:
            response = None

        if response is None:
            raise ResponseTimeoutError('Waiting for the response from the {!r} request timed '
                                       'out after {} seconds'.format(method32, self._rpc_timeout))

        if response.status == OK:
            with open(self._pickle_path, 'rb') as f:
                result = pickle.load(f)
            return result

        raise Server32Error(**json.loads(response.read().decode(encoding='utf-8', errors='replace')))

    def shutdown_server32(self, kill_timeout=10):
        """Shutdown the 32-bit server.

        This method shuts down the 32-bit server, closes the client connection
        and it deletes the temporary file that is used to save the serialized
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
            The (stdout, stderr) streams from the 32-bit server.

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

        # give the server a chance to shut down gracefully
        t0 = time.time()
        while self._proc.poll() is None:
            time.sleep(0.1)
            if time.time() - t0 > kill_timeout:
                self._proc.terminate()
                self._proc.returncode = -1
                warnings.warn('killed the 32-bit server using brute force', stacklevel=2)
                break

        # the frozen 32-bit server can still block the process from terminating
        # the <signal.SIGKILL 9> constant is not available on Windows
        if self._meta32:
            try:
                os.kill(self._meta32['pid'], 9)
            except OSError:
                pass  # the server has already stopped

        if os.path.isfile(self._pickle_path):
            os.remove(self._pickle_path)

        self._conn.close()
        self._conn = None
        return self._proc.stdout, self._proc.stderr

    def __del__(self):
        if self._conn is not None:
            self.shutdown_server32()
