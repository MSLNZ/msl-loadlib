"""
Load a shared library.
"""
import os
import sys
import ctypes
import ctypes.util
import subprocess

from . import (
    utils,
    DEFAULT_EXTENSION,
    IS_PYTHON2,
)

_encoding = sys.getfilesystemencoding()


class LoadLibrary(object):

    LIBTYPES = ['cdll', 'windll', 'oledll', 'net', 'clr', 'java', 'com', 'activex']
    """The library types that are supported."""

    def __init__(self, path, libtype=None, **kwargs):
        """Load a shared library.

        For example, a C/C++, FORTRAN, C#, Java, Delphi, LabVIEW, ActiveX, ... library.

        .. versionchanged:: 0.4
           Added support for Java archives.

        .. versionchanged:: 0.5
           Added support for COM_ libraries.

        .. versionchanged:: 0.9
           Added support for ActiveX_ libraries.

        .. _Assembly: https://docs.microsoft.com/en-us/dotnet/api/system.reflection.assembly
        .. _comtypes.CreateObject: https://pythonhosted.org/comtypes/#creating-and-accessing-com-objects
        .. _COM: https://en.wikipedia.org/wiki/Component_Object_Model
        .. _ActiveX: https://en.wikipedia.org/wiki/ActiveX

        Parameters
        ----------
        path : :class:`str`
            The path to the shared library.

            The search order for finding the shared library is:

                1. assume that a full or a relative (to the current working directory)
                   path is specified,
                2. use :func:`ctypes.util.find_library` to find the shared library file,
                3. search :data:`sys.path`, then
                4. search :data:`os.environ['PATH'] <os.environ>` to find the shared library.

            If loading a COM_ library then `path` is either the `ProgID`, e.g.
            ``"InternetExplorer.Application"``, or the `CLSID`, e.g.
            ``"{2F7860A2-1473-4D75-827D-6C4E27600CAC}"``.

        libtype : :class:`str`, optional
            The library type. The following values are currently supported:

            * ``'cdll'`` -- for a library that uses the __cdecl calling convention
            * ``'windll'`` or ``'oledll'`` -- for a __stdcall calling convention
            * ``'net'`` or ``'clr'`` -- for Microsoft's .NET Framework (Common Language Runtime)
            * ``'java'`` -- for a Java archive, ``.jar``, or Java byte code, ``.class``, file
            * ``'com'`` -- for a COM_ library
            * ``'activex'`` -- for an ActiveX_ library

            Default is ``'cdll'``.

            .. tip::
               Since the ``.jar`` or ``.class`` extension uniquely defines a Java library,
               the `libtype` will be automatically set to ``'java'`` if `path` ends with
               ``.jar`` or ``.class``.

        **kwargs
            All additional keyword arguments are passed to the object that loads the library.

            If `libtype` is

                * ``'cdll'`` then :class:`~ctypes.CDLL`
                * ``'windll'`` then :class:`~ctypes.WinDLL`
                * ``'oledll'`` then :class:`~ctypes.OleDLL`
                * ``'net'`` or ``'clr'`` then all keyword arguments are ignored
                * ``'java'`` then :class:`~.py4j.java_gateway.JavaGateway`
                * ``'com'`` then comtypes.CreateObject_
                * ``'activex'`` then :meth:`Application.load <msl.loadlib.activex.Application.load>`

        Raises
        ------
        OSError
            If the shared library cannot be loaded.
        ValueError
            If the value of `libtype` is not supported.
        """
        # a reference to the shared library
        self._lib = None

        # a reference to the .NET Runtime Assembly
        self._assembly = None

        # a reference to the Py4J JavaGateway
        self._gateway = None

        if not path:
            raise ValueError('You must specify the path, got {!r}'.format(path))

        # fixes Issue #8, if `path` is a <class 'pathlib.Path'> object
        if hasattr(path, 'as_posix'):
            path = path.as_posix()

        # try to automatically determine the libtype
        if libtype is None:
            if path.endswith('.jar') or path.endswith('.class'):
                libtype = 'java'
            else:
                libtype = 'cdll'
        else:
            libtype = libtype.lower()

        if libtype not in LoadLibrary.LIBTYPES:
            raise ValueError(
                'Cannot load libtype={!r}.\n'
                'Must be one of: {}'.format(libtype, ', '.join(LoadLibrary.LIBTYPES))
            )

        # create a new reference to `path` just in case the
        # DEFAULT_EXTENSION is appended below so that the
        # ctypes.util.find_library function call will use the
        # unmodified value of `path`
        _path = path

        # assume a default extension if no extension was provided
        ext = os.path.splitext(path)[1]
        if not ext and libtype not in ['java', 'com', 'activex']:
            _path += DEFAULT_EXTENSION

        if IS_PYTHON2:
            _path = _path.encode(_encoding)

        if libtype not in ['com', 'activex']:
            self._path = os.path.abspath(_path)
            if not os.path.isfile(self._path):
                # for find_library use the original 'path' value since it may be a library name
                # without any prefix like 'lib', suffix like '.so', '.dylib' or version number
                self._path = ctypes.util.find_library(path)
                if self._path is None:  # then search sys.path and os.environ['PATH']
                    success = False
                    search_dirs = sys.path + os.environ['PATH'].split(os.pathsep)
                    for directory in search_dirs:
                        p = os.path.join(directory, _path)
                        if os.path.isfile(p):
                            self._path = p
                            success = True
                            break
                    if not success:
                        raise OSError("Cannot find '{}' for libtype='{}'".format(path, libtype))
        else:
            self._path = _path

        if libtype == 'cdll':
            self._lib = ctypes.CDLL(self._path, **kwargs)
        elif libtype == 'windll':
            self._lib = ctypes.WinDLL(self._path, **kwargs)
        elif libtype == 'oledll':
            self._lib = ctypes.OleDLL(self._path, **kwargs)
        elif libtype == 'com':
            if not utils.is_comtypes_installed():
                raise OSError(
                    'Cannot load a COM library because comtypes is not installed.\n'
                    'Run: pip install comtypes'
                )

            from comtypes import GUID
            from comtypes.client import CreateObject

            try:
                clsid = GUID.from_progid(self._path)
            except (TypeError, OSError):
                clsid = None

            if clsid is None:
                raise OSError("Cannot find '{}' for libtype='com'".format(path))

            self._lib = CreateObject(clsid, **kwargs)

        elif libtype == 'activex':
            from .activex import Application
            self._lib = Application.load(self._path, **kwargs)

        elif libtype == 'java':
            if not utils.is_py4j_installed():
                raise OSError(
                    'Cannot load a Java file because Py4J is not installed.\n'
                    'Run: pip install py4j'
                )

            from py4j.version import __version__
            from py4j.java_gateway import JavaGateway, GatewayParameters

            # the address and port to use to host the py4j.GatewayServer
            address = kwargs.pop('address', '127.0.0.1')
            port = kwargs.pop('port', utils.get_available_port())

            # find the py4j JAR (needed to import py4j.GatewayServer on the Java side)
            root = os.path.dirname(sys.executable)
            filename = 'py4j'+__version__+'.jar'
            py4j_jar = os.path.join(root, 'share', 'py4j', filename)
            if not os.path.isfile(py4j_jar):
                root = os.path.dirname(root)  # then check one folder up (for unix or venv)
                py4j_jar = os.path.join(root, 'share', 'py4j', filename)
                if not os.path.isfile(py4j_jar):
                    py4j_jar = os.environ.get('PY4J_JAR', '')  # then check the environment variable
                    if not os.path.isfile(py4j_jar):
                        raise OSError(
                            'Cannot find {0}\nCreate a PY4J_JAR environment '
                            'variable to be equal to the full path to {0}'.format(filename)
                        )

            # build the java command
            wrapper = os.path.join(os.path.dirname(__file__), 'py4j-wrapper.jar')
            cmd = ['java', '-cp', py4j_jar + os.pathsep + wrapper, 'Py4JWrapper', str(port)]

            # from the URLClassLoader documentation:
            #   Any URL that ends with a '/' is assumed to refer to a directory. Otherwise, the URL
            #   is assumed to refer to a JAR file which will be downloaded and opened as needed.
            if ext == '.jar':
                cmd.append(self._path)
            else:  # it is a .class file
                cmd.append(os.path.dirname(self._path) + '/')

            try:
                # start the py4j.GatewayServer
                subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                err = None
            except OSError as e:
                err = str(e) + '\nYou must have a Java Runtime Environment installed and available on PATH'

            if err:
                raise OSError(err)

            utils.wait_for_server(address, port, 5.0)

            self._gateway = JavaGateway(
                gateway_parameters=GatewayParameters(address=address, port=port, **kwargs)
            )

            self._lib = self._gateway.jvm

        elif libtype == 'net' or libtype == 'clr':
            if not utils.is_pythonnet_installed():
                raise OSError(
                    'Cannot load a .NET Assembly because pythonnet is not installed.\n'
                    'Run: pip install pythonnet'
                )

            import clr
            import System
            dotnet = {'System': System}

            # the shared library must be available in sys.path
            head, tail = os.path.split(self._path)
            sys.path.insert(0, head)

            try:
                # don't include the library extension
                clr.AddReference(os.path.splitext(tail)[0])
            except System.IO.FileNotFoundException:
                # The file must exist since its existence is checked above.
                # There must be another reason why loading the DLL raises this
                # error. Calling LoadFile (below) provides more information
                # in the error message.
                pass

            try:
                # By default, pythonnet can only load libraries that are for .NET 4.0+
                #
                # In order to allow pythonnet to load a library from .NET <4.0 the
                # useLegacyV2RuntimeActivationPolicy property needs to be enabled
                # in a <python-executable>.config file. If the following statement
                # raises a FileLoadException then attempt to create the configuration
                # file that has the property enabled and then notify the user why
                # loading the library failed and ask them to re-run their Python
                # script to load the .NET library.
                self._assembly = System.Reflection.Assembly.LoadFile(self._path)

            except System.IO.FileLoadException as err:
                # Example error message that can occur if the library is for .NET <4.0,
                # and the useLegacyV2RuntimeActivationPolicy is not enabled:
                #
                # " Mixed mode assembly is built against version 'v2.0.50727' of the
                #  runtime and cannot be loaded in the 4.0 runtime without additional
                #  configuration information. "
                if str(err).startswith('Mixed mode assembly is built against version'):
                    status, msg = utils.check_dot_net_config(sys.executable)
                    if not status == 0:
                        raise OSError(msg)
                    else:
                        update_msg = 'Checking .NET config returned "{}" '.format(msg)
                        update_msg += 'and still cannot load library.\n'
                        update_msg += str(err)
                        raise OSError(update_msg)
                raise OSError('The above "System.IO.FileLoadException" is not handled.\n')

            try:
                types = self._assembly.GetTypes()
            except Exception as e:
                utils.logger.error(e)
                utils.logger.error('The LoaderExceptions are:')
                for item in e.LoaderExceptions:
                    utils.logger.error('  ' + item.Message)
            else:
                for t in types:
                    try:
                        if t.Namespace:
                            obj = __import__(t.Namespace)
                        else:
                            obj = getattr(__import__('clr'), t.FullName)
                    except:
                        obj = t
                        obj.__name__ = t.FullName

                    if obj.__name__ not in dotnet:
                        dotnet[obj.__name__] = obj

            self._lib = DotNet(dotnet, self._path)

        else:
            assert False, 'Should not get here -- contact developers'

        if IS_PYTHON2:
            self._path = self._path.decode(_encoding)

        utils.logger.debug('Loaded ' + self._path)

    def __repr__(self):
        path = self._path.encode(_encoding) if IS_PYTHON2 else self._path
        return '<LoadLibrary libtype={} path={}>'.format(self._lib.__class__.__name__, path)

    def __del__(self):
        if self._gateway is not None:
            self._gateway.shutdown()
            utils.logger.debug('shutdown py4j.GatewayServer')

    @property
    def assembly(self):
        """
        Returns a reference to the `.NET Runtime Assembly <Assembly_>`_ object if
        the shared library is a .NET Framework otherwise returns :data:`None`.

        .. tip::
           The `JetBrains dotPeek`_ program can be used to reliably decompile any
           .NET Assembly into the equivalent source code.

        .. _JetBrains dotPeek: https://www.jetbrains.com/decompiler/
        """
        return self._assembly

    @property
    def gateway(self):
        """
        Returns the :class:`~py4j.java_gateway.JavaGateway` object, only if
        the shared library is a Java archive, otherwise returns :data:`None`.
        """
        return self._gateway

    @property
    def lib(self):
        """Returns the reference to the loaded library object.

        For example, if `libtype` is

            * ``'cdll'`` then a :class:`~ctypes.CDLL` object
            * ``'windll'`` then a :class:`~ctypes.WinDLL` object
            * ``'oledll'`` then a :class:`~ctypes.OleDLL` object
            * ``'net'`` or ``'clr'`` then a :class:`~.load_library.DotNet` object
            * ``'java'`` then a :class:`~py4j.java_gateway.JVMView` object
            * ``'com'`` or ``'activex'`` then an interface pointer to the COM_ object
        """
        return self._lib

    @property
    def path(self):
        """:class:`str`: The path to the shared library file."""
        return self._path


class DotNet(object):

    def __init__(self, dot_net_dict, path):
        """Contains the namespace_ modules, classes and `System.Type`_ objects of a .NET Assembly.

        Do not instantiate this class directly.

        .. _namespace: https://msdn.microsoft.com/en-us/library/z2kcy19k.aspx
        .. _System.Type: https://docs.microsoft.com/en-us/dotnet/api/system.type
        """
        self.__dict__.update(dot_net_dict)
        self._path = path

    def __repr__(self):
        return '<{} path={}>'.format(self.__class__.__name__, self._path)
