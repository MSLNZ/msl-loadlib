"""
Contains the base class for communicating with a 32-bit library from 64-bit Python.

The :class:`~.server32.Server32` class is used in combination with the
:class:`~.client64.Client64` class to communicate with a 32-bit shared library
from 64-bit Python.
"""
import os
import sys
import site
import uuid
import time
import random
import tempfile
import subprocess
try:
    import cPickle as pickle
except ImportError:
    import pickle

from msl.loadlib import IS_PYTHON2, IS_PYTHON3, SERVER_FILENAME

if IS_PYTHON2:
    from httplib import HTTPConnection
    from httplib import HTTPException
elif IS_PYTHON3:
    from http.client import HTTPConnection
    from http.client import HTTPException
else:
    raise NotImplementedError('Python major version is not 2 or 3')


class Client64(HTTPConnection):
    """
    All classes that want to communicate with a 32-bit library must be inherited
    from this class.

    Starts a 32-bit server, :class:`~.server32.Server32`, to host a Python module
    that is a wrapper around a 32-bit library. The *client* module runs within
    a 64-bit Python interpreter and it sends a request to the server which calls
    the 32-bit library to execute the request. The server then provides a
    response back to the client.

    Args:
        module32 (str): The name of the Python module that is to be imported by
            the 32-bit server.

        host (str, optional): The IP address of the 32-bit server. Default is '127.0.0.1'.

        port (int, optional): The port to open on the 32-bit server. Default is :py:data:`None`
            (which means to automatically find a port that is available).

        timeout (float, optional): The maximum number of seconds to wait to establish a
            connection to the 32-bit server. Default is 10.0.

        quiet (bool, optional): Whether to hide :py:data:`sys.stdout` messages from
            the 32-bit server. Default is :py:data:`True`.

        append_path (str, list[str], optional): Append
            path(s) to the 32-bit server's :py:data:`sys.path` list of paths.
            Default is :py:data:`None`.

            For example, to add a single path

                append_path = 'D:/code/scripts'

            and to add multiple paths

                append_path = ['D:/code/scripts', 'D:/code/libs', 'D:/modules']

            .. note::
                If ``module32`` is not located in the same folder as the *client* module
                then you must either specify the full path to ``module32`` **or** you can
                specify the folder where ``module32`` is located by passing a value to the
                ``append_path`` argument. Using the ``append_path`` option also allows
                for any other modules that ``module32`` may depend on to also be included
                in :py:data:`sys.path` so that those modules can be imported when ``module32``
                is imported.

    Raises:
        IOError: If the frozen executable cannot be found.
        :py:class:`~http.client.HTTPException`: If the connection to the 32-bit server cannot
            be established.
    """
    def __init__(self, module32, host='127.0.0.1', port=None, timeout=10.0,
                 quiet=True, append_path=None):

        self._is_active = False

        if port is None:
            while True:
                port = random.randint(1024, 65535)
                if not self._port_in_use(port):
                    break

        # the temporary file to use to save the pickle'd data
        self._pickle_temp_file = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))

        # select the highest-level pickle protocol to use based on the version of python
        major, minor = sys.version_info.major, sys.version_info.minor
        if (major <= 1) or (major == 2 and minor < 3):
            self._pickle_protocol = 1
        elif major == 2:
            self._pickle_protocol = 2
        elif (major == 3) and (minor < 4):
            self._pickle_protocol = 3
        else:
            self._pickle_protocol = pickle.HIGHEST_PROTOCOL

        # make sure that the server32 executable exists
        server_exe = os.path.join(os.path.dirname(__file__), SERVER_FILENAME)
        if not os.path.isfile(server_exe):
            msg = 'Cannot find {}\n'.format(server_exe)
            msg += 'To create a 32-bit Python server run:\n'
            msg += '>>> from msl.loadlib import freeze_server32\n'
            msg += '>>> freeze_server32.main()'
            raise IOError(msg)

        cmd = [server_exe,
               '--module', module32,
               '--host', host,
               '--port', str(port)
               ]

        # include folders to the 32-bit server's sys.path
        _append_path = site.getsitepackages()
        if append_path is not None:
            if isinstance(append_path, str):
                _append_path.append(append_path)
            else:
                _append_path.extend(append_path)
        cmd.extend(['--append-path', '[' + ','.join(_append_path) + ']'])

        if quiet:
            cmd.append('--quiet')

        # start the server, cannot use subprocess.call() because it blocks
        subprocess.Popen(cmd, stderr=sys.stderr, stdout=sys.stderr)

        # wait for the server to be running -- essentially this is the subprocess.wait() method
        stop = time.time() + max(0.0, timeout)
        while True:
            if self._port_in_use(port):
                break
            if time.time() > stop:
                m = 'Timeout after {:.1f} s. Could not connect to {}:{}'.format(timeout, host, port)
                raise HTTPException(m)

        # start the connection
        HTTPConnection.__init__(self, host, port)
        self._is_active = True

    def __repr__(self):
        msg = '{} object at {}'.format(self.__class__.__name__, hex(id(self)))
        if self._is_active:
            lib = os.path.basename(self.lib32_path)
            return msg + ' hosting {} on http://{}:{}'.format(lib, self.host, self.port)
        else:
            return msg + ' has stopped the server'

    @property
    def lib32_path(self):
        """
        Returns:
            :py:class:`str`: The absolute path to the 32-bit shared-library file.
        """
        return self.request32('LIB32_PATH')

    def request32(self, method32, *args, **kwargs):
        """
        Send a request to the 32-bit server.

        Args:
            method32 (str): The name of the method to call in the
                :class:`~.server32.Server32` subclass.

            *args: The arguments that the ``method32`` method in the
                :class:`~.server32.Server32` subclass requires.

            **kwargs: The keyword arguments that the ``method32`` method in the
                :class:`~.server32.Server32` subclass requires.

        Returns:
            The response from the 32-bit server.

        Raises:
            :py:class:`~http.client.HTTPException`: If there was an error
                processing the request on the 32-bit server.
        """
        if not self._is_active:
            raise HTTPException('The server is not active')

        if method32 == 'SHUTDOWN_SERVER':
            self.request('GET', '/' + method32)
            return

        request = '/{}:{}:{}'.format(method32, self._pickle_protocol, self._pickle_temp_file)
        with open(self._pickle_temp_file, 'wb') as f:
            pickle.dump(args, f, protocol=self._pickle_protocol)
            pickle.dump(kwargs, f, protocol=self._pickle_protocol)
        self.request('GET', request)

        response = self.getresponse()
        if response.status == 200:  # everything is OK
            with open(self._pickle_temp_file, 'rb') as f:
                result = pickle.load(f)
            return result
        raise HTTPException(response.read().decode())

    def shutdown_server(self):
        """
        Shut down the server and delete the temporary file that is used to save the
        serialized :py:mod:`pickle`\'d data which is passed between the 32-bit server
        and the 64-bit client.

        .. note::
           This method gets called automatically when the :class:`~.client64.Client64`
           object gets destroyed.
        """
        if self._is_active:
            self.request32('SHUTDOWN_SERVER')
            if os.path.isfile(self._pickle_temp_file):
                os.remove(self._pickle_temp_file)
            self.close()
            self._is_active = False

    def __del__(self):
        self.shutdown_server()

    def _port_in_use(self, port):
        """
        Uses 'netstat' to determine if the port is in use.
        """
        p = subprocess.Popen(['netstat', '-an'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p.communicate()[0].decode().find(':{} '.format(port)) > 0
