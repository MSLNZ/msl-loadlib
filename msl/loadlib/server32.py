"""
Contains the base class for loading a 32-bit shared library in 32-bit Python.

The :class:`~.server32.Server32` class is used in combination with the
:class:`~.client64.Client64` class to communicate with a 32-bit shared library
from 64-bit Python.
"""
import os
import re
import sys
import json
import warnings
import traceback
import threading
import subprocess
try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import pickle
except ImportError:  # then Python 2
    import cPickle as pickle
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from . import (
    LoadLibrary,
    SERVER_FILENAME,
    IS_WINDOWS,
)

METADATA = '-METADATA-'
SHUTDOWN = '-SHUTDOWN-'
OK = 200
ERROR = 500


class Server32(HTTPServer):

    def __init__(self, path, libtype, host, port, *args, **kwargs):
        """Base class for loading a 32-bit library in 32-bit Python.

        All modules that are to be run on the 32-bit server must contain a class
        that is inherited from this class and the module can import **any** of
        the `standard`_ python modules **except** for :mod:`distutils`,
        :mod:`ensurepip`, :mod:`tkinter` and :mod:`turtle`.

        All modules that are run on the 32-bit server must be able to run on the Python
        interpreter that the server is running on, see :meth:`.version` for how to
        determine the version of the Python interpreter.

        .. _standard: https://docs.python.org/3/py-modindex.html
        .. _JVM: https://en.wikipedia.org/wiki/Java_virtual_machine

        Parameters
        ----------
        path : :class:`str`
            The path to the 32-bit library. See :class:`.LoadLibrary` for more details.
        libtype : :class:`str`
            The library type. See :class:`.LoadLibrary` for more details.

            .. note::
               Since Java byte code is executed on the JVM_ it does not make sense to
               use :class:`Server32` for a Java ``.jar`` or ``.class`` file.

        host : :class:`str`
            The IP address of the server.
        port : :class:`int`
            The port to run the server on.
        *args
            All additional arguments are currently ignored.
        **kwargs
            All keyword arguments are passed to :class:`.LoadLibrary`.
        """
        self._library = LoadLibrary(path, libtype=libtype, **kwargs)
        self._assembly = self._library.assembly
        self._lib = self._library.lib
        self._path = self._library.path
        super(Server32, self).__init__((host, int(port)), _RequestHandler)

    @property
    def assembly(self):
        """
        Returns a reference to the `.NET Runtime Assembly <NET_>`_ object if
        the shared library is a .NET Framework otherwise returns :data:`None`.

        .. tip::
           The `JetBrains dotPeek`_ program can be used to reliably decompile any
           .NET Assembly into the equivalent source code.

        .. _NET: https://docs.microsoft.com/en-us/dotnet/api/system.reflection.assembly
        .. _JetBrains dotPeek: https://www.jetbrains.com/decompiler/
        """
        return self._assembly

    @property
    def lib(self):
        """Returns the reference to the 32-bit, loaded-library object.

        For example, if `libtype` is

            * ``'cdll'`` then a :class:`~ctypes.CDLL` object
            * ``'windll'`` then a :class:`~ctypes.WinDLL` object
            * ``'oledll'`` then a :class:`~ctypes.OleDLL` object
            * ``'net'`` or ``'clr'`` then a :class:`~.load_library.DotNet` object
            * ``'com'`` or ``'activex'`` then an interface pointer to the COM_ object

        .. _COM: https://en.wikipedia.org/wiki/Component_Object_Model
        """
        return self._lib

    @property
    def path(self):
        """:class:`str`: The path to the shared library file."""
        return self._path

    @staticmethod
    def version():
        """Gets the version of the Python interpreter that the 32-bit server is running on.

        Returns
        -------
        :class:`str`
            The result of executing ``'Python ' + sys.version`` on the 32-bit server.


        .. invisible-code-block: pycon

           >>> SKIP_IF_MACOS()

        Examples
        --------
        ::

            >>> from msl.loadlib import Server32
            >>> Server32.version()
            'Python 3.7.10 ...'

        Note
        ----
        This method takes about 1 second to finish because the 32-bit server
        needs to start in order to determine the version of the Python interpreter.
        """
        exe = os.path.join(os.path.dirname(__file__), SERVER_FILENAME)
        pipe = subprocess.Popen([exe, '--version'], stdout=subprocess.PIPE)
        return pipe.communicate()[0].decode().strip()

    @staticmethod
    def interactive_console():
        """Start an interactive console.

        This method starts an interactive console, in a new terminal, with the
        Python interpreter on the 32-bit server.

        Examples
        --------
        ::

            >>> from msl.loadlib import Server32  # doctest: +SKIP
            >>> Server32.interactive_console()  # doctest: +SKIP
        """
        exe = os.path.join(os.path.dirname(__file__), SERVER_FILENAME)
        if IS_WINDOWS:
            cmd = 'start "msl.loadlib.Server32 || interactive console" "{exe}" --interactive'
        else:
            cmd = "gnome-terminal --command='{exe} --interactive'"
        os.system(cmd.format(exe=exe))

    @property
    def quiet(self):
        """This attribute is no longer used and it will be removed in a future release.

        Returns :data:`True`.
        """
        warnings.simplefilter('once', DeprecationWarning)
        warnings.warn(
            'The `quiet` attribute for Server32 will be removed in a future release -- always returns True',
            DeprecationWarning,
            stacklevel=2
        )
        return True

    @staticmethod
    def remove_site_packages_64bit():
        """Remove the site-packages directory from the 64-bit process.

        By default the site-packages directory of the 64-bit process is
        included in :data:`sys.path` of the 32-bit process. Having the
        64-bit site-packages directory available can sometimes cause issues.
        For example, comtypes imports numpy so if numpy is installed in the
        64-bit process then comtypes will import the 64-bit version of numpy
        in the 32-bit process. Depending on the version of Python and/or numpy
        this can cause the 32-bit server to crash.

        .. versionadded:: 0.9

        Examples
        --------
        ::

            import sys
            from msl.loadlib import Server32

            class FileSystem(Server32):

                def __init__(self, host, port, **kwargs):

                    # remove the site-packages directory that was passed from 64-bit Python
                    # before calling the super() function to load the COM library
                    path = Server32.remove_site_packages_64bit()

                    super(FileSystem, self).__init__('Scripting.FileSystemObject', 'com', host, port)

                    # optional: add the site-packages directory back into sys.path
                    sys.path.append(path)

        Returns
        -------
        :class:`str`
            The path of the site-packages directory that was removed. Can be an
            empty string if the directory was not found in :data:`sys.path`.
        """
        for index, path in enumerate(sys.path):
            if path.endswith('site-packages'):
                return sys.path.pop(index)
        return ''

    @staticmethod
    def is_interpreter():
        """Check if code is running on the 32-bit server.

        If the same module is executed by both
        :class:`~msl.loadlib.client64.Client64` and :class:`.Server32`
        then there may be only parts of the code that should be executed
        by the correct bitness of the Python interpreter.

        .. versionadded:: 0.9

        Returns
        -------
        :class:`bool`
            Whether the code is running on the 32-bit server.

        Examples
        --------
        ::

            import sys
            from msl.loadlib import Server32

            if Server32.is_interpreter():
                # this only gets executed on the 32-bit server
                assert sys.maxsize < 2**32

        """
        return sys.executable.endswith(SERVER_FILENAME)

    @staticmethod
    def examples_dir():
        """Get the directory where the example libraries are located.

        .. versionadded:: 0.9

        Returns
        -------
        :class:`str`
            The directory where the example libraries are located.
        """
        if Server32.is_interpreter():
            root = os.path.dirname(sys.executable)
        else:
            root = os.path.dirname(__file__)
        path = os.path.join(root, os.pardir, 'examples', 'loadlib')
        return os.path.abspath(path)

    def shutdown_handler(self):
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
                response = {'path': self.server.path, 'pid': os.getpid()}
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

        except Exception as e:
            print('{}: {}'.format(e.__class__.__name__, e))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_list = traceback.extract_tb(exc_traceback)
            tb = tb_list[min(len(tb_list)-1, 1)]  # get the Server32 subclass exception
            response = {'name': exc_type.__name__, 'value': str(exc_value)}
            traceback_ = '  File {!r}, line {}, in {}'.format(tb[0], tb[1], tb[2])
            if tb[3]:
                traceback_ += '\n    {}'.format(tb[3])
            response['traceback'] = traceback_
            self.send_response(ERROR)
            self.end_headers()
            self.wfile.write(json.dumps(response).encode(encoding='utf-8', errors='ignore'))

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

    def log_message(self, fmt, *args):
        """
        Overrides: :meth:`~http.server.BaseHTTPRequestHandler.log_message`

        Ignore all log messages from being displayed in :data:`sys.stdout`.
        """
        pass
