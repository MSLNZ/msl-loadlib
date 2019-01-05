"""
Contains the base class for loading a 32-bit shared library in 32-bit Python.

The :class:`~.server32.Server32` class is used in combination with the
:class:`~.client64.Client64` class to communicate with a 32-bit shared library
from 64-bit Python.
"""
import os
import sys
import json
import traceback
import threading
import subprocess
try:
    import cPickle as pickle  # Python 2
except ImportError:
    import pickle
try:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler  # Python 2
except ImportError:
    from http.server import HTTPServer, BaseHTTPRequestHandler

from . import LoadLibrary, SERVER_FILENAME, IS_WINDOWS


class Server32(HTTPServer):

    def __init__(self, path, libtype, host, port, quiet, **kwargs):
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
            The path to the 32-bit library.
        libtype : :class:`str`
            The library type to use for the calling convention. One of the following:

                * ``'cdll'`` -- for a __cdecl library
                * ``'windll'`` or ``'oledll'`` -- for a __stdcall library (Windows only)
                * ``'net'`` or ``'clr'`` -- for Microsoft's .NET Framework (Common Language Runtime)
                * ``'com'`` -- for a `COM <https://en.wikipedia.org/wiki/Component_Object_Model>`_ library.

            .. note::
               Since Java byte code is executed on the JVM_ it does not make sense to
               use :class:`Server32` for a Java ``.jar`` or ``.class`` file.

        host : :class:`str`
            The IP address of the server.
        port : :class:`int`
            The port to open on the server.
        quiet : :class:`bool`
            Whether to hide :data:`sys.stdout` messages on the server.
        **kwargs
            Keyword arguments that are passed to :class:`.LoadLibrary`.

        Raises
        ------
        IOError
            If the shared library cannot be loaded.
        TypeError
            If the value of `libtype` is not supported.
        """
        self._quiet = bool(quiet)
        self._library = LoadLibrary(path, libtype=libtype, **kwargs)
        super(Server32, self).__init__((host, int(port)), RequestHandler)

    @property
    def assembly(self):
        """
        Returns a reference to the `.NET Runtime Assembly <NET_>`_ object, *only if
        the shared library is a .NET Framework*, otherwise returns :data:`None`.

        .. tip::
           The `JetBrains dotPeek`_ program can be used to reliably decompile any
           .NET Assembly in to the equivalent source code.

        .. _NET: https://msdn.microsoft.com/en-us/library/system.reflection.assembly(v=vs.110).aspx
        .. _JetBrains dotPeek: https://www.jetbrains.com/decompiler/
        """
        return self._library.assembly

    @property
    def lib(self):
        """Returns the reference to the 32-bit, loaded library object.

        For example, if `libtype` is

        * ``'cdll'`` then a :class:`~ctypes.CDLL` object
        * ``'windll'`` then a :class:`~ctypes.WinDLL` object
        * ``'oledll'`` then a :class:`~ctypes.OleDLL` object
        * ``'net'`` or ``'clr'`` then a :class:`~.load_library.DotNet` object
        * ``'com'`` then the interface pointer returned by comtypes.CreateObject_

        .. _comtypes.CreateObject: https://pythonhosted.org/comtypes/#creating-and-accessing-com-objects
        """
        return self._library.lib

    @property
    def path(self):
        """:class:`str`: The path to the shared library file."""
        return self._library.path

    @staticmethod
    def version():
        """Gets the version of the Python interpreter that the 32-bit server is running on.

        Returns
        -------
        :class:`str`
            The result of executing ``'Python ' + sys.version`` on the 32-bit server.

        Examples
        --------
        ::

            >>> from msl.loadlib import Server32
            >>> Server32.version()  # doctest: +SKIP
            Python 3.6.8 (tags/v3.6.8:3c6b436a57, Dec 23 2018, 23:31:17) [MSC v.1916 32 bit (Intel)]

        Note
        ----
        This method takes about 1 second to finish because the server executable
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

            >>> from msl.loadlib import Server32
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
        """:class:`bool`: Whether :data:`sys.stdout` messages are hidden on the server."""
        return self._quiet


class RequestHandler(BaseHTTPRequestHandler):
    """Handles the request that was sent to the 32-bit server."""

    def do_GET(self):
        """Handle a GET request."""
        request = self.path[1:]
        if request == 'SHUTDOWN_SERVER32':
            threading.Thread(target=self.server.shutdown).start()
            return

        try:
            method, pickle_protocol, pickle_temp_file = request.split(':', 2)
            if method == 'LIB32_PATH':
                response = self.server.path
            else:
                with open(pickle_temp_file, 'rb') as f:
                    args = pickle.load(f)
                    kwargs = pickle.load(f)
                response = getattr(self.server, method)(*args, **kwargs)

            with open(pickle_temp_file, 'wb') as f:
                pickle.dump(response, f, protocol=int(pickle_protocol))

            self.send_response(200)
            self.end_headers()

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_list = traceback.extract_tb(exc_traceback)
            tb = tb_list[min(len(tb_list)-1, 1)]  # get the Server32 subclass exception

            response = {'name': exc_type.__name__, 'value': str(exc_value)}
            traceback_ = '  File "{}", line {}, in {}'.format(tb[0], tb[1], tb[2])
            if tb[3]:
                traceback_ += '\n    {}'.format(tb[3])
            response['traceback'] = traceback_

            self.send_response(501)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode(encoding='utf-8', errors='ignore'))

    def log_message(self, fmt, *args):
        """
        Overrides: :meth:`~http.server.BaseHTTPRequestHandler.log_message`

        Ignore all log messages from being displayed in :data:`sys.stdout`.
        """
        pass
