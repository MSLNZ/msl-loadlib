"""
Load a shared library.
"""
import os
import sys
import ctypes
import ctypes.util
import logging
import subprocess

from msl.loadlib import utils
from msl.loadlib import DEFAULT_EXTENSION

logger = logging.getLogger(__name__)


class LoadLibrary(object):

    def __init__(self, path, libtype='cdll'):
        """Load a shared library.

        For example, a C/C++, FORTRAN, CLR, Java, Delphi, LabVIEW, ... library.

        Based on the value of `libtype` or the file extension this class will load the
        shared library as a:

            * :class:`~ctypes.CDLL` if `libtype` is ``'cdll'``,
            * :class:`~ctypes.WinDLL` if `libtype` is ``'windll'``,
            * :class:`~ctypes.OleDLL` if `libtype` is ``'oledll'``,
            * `System.Reflection.Assembly <Assembly_>`_ if `libtype` is ``'net'``, or a
            * :class:`~.py4j.java_gateway.JavaGateway` if `libtype` is ``'java'``.

        .. _Assembly: https://msdn.microsoft.com/en-us/library/system.reflection.assembly(v=vs.110).aspx

        Parameters
        ----------
        path : :class:`str`
            The path to the shared library.

            The search order for finding the shared library is:

                1. assume that a full or a relative (to the current working directory)
                   path is specified,
                2. use :obj:`ctypes.util.find_library` to find the shared library file,
                3. search :obj:`sys.path`, then
                4. search :obj:`os.environ['PATH'] <os.environ>` to find the shared library.

        libtype : :class:`str`, optional
            The library type. The following values are currently supported:

            * ``'cdll'`` -- for a library that uses the __cdecl calling convention
            * ``'windll'`` or ``'oledll'`` -- for a __stdcall calling convention
            * ``'net'`` -- for Microsoft's .NET Framework (Common Language Runtime)
            * ``'java'`` -- for a Java archive, ``.jar``, or Java byte code, ``.class``, file

            Default is ``'cdll'``.

            .. note::
               Since the ``.jar`` or ``.class`` extension uniquely defines a Java library,
               the `libtype` will automatically be set to ``'java'`` if `path` ends with
               ``.jar`` or ``.class``.

        Raises
        ------
        IOError
            If the shared library cannot be loaded.
        TypeError
            If `libtype` is not a supported library type.
        """

        # a reference to the shared library
        self._lib = None

        # a reference to the .NET Runtime Assembly
        self._assembly = None

        # a reference to the Py4J JavaGateway
        self._gateway = None

        # fixes Issue #8, if `path` is a <class 'pathlib.Path'> object
        path = str(path)

        # create a new reference to `path` just in case the
        # DEFAULT_EXTENSION is appended below so that the
        # ctypes.util.find_library function call will use the
        # unmodified value of `path`
        _path = path

        # assume a default extension if no extension was provided
        ext = os.path.splitext(_path)[1]
        if not ext:
            _path += DEFAULT_EXTENSION

        # the .jar or .class extension uniquely defines a Java library
        if ext in ('.jar', '.class'):
            libtype = 'java'

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
                    raise IOError('Cannot find the shared library "{}"'.format(path))

        libtype = libtype.lower()
        if libtype == 'cdll':
            self._lib = ctypes.CDLL(self._path)
        elif libtype == 'windll':
            self._lib = ctypes.WinDLL(self._path)
        elif libtype == 'oledll':
            self._lib = ctypes.OleDLL(self._path)
        elif libtype == 'java':
            if not utils.is_py4j_installed():
                raise IOError('Cannot load a Java file because Py4J is not installed.\n'
                              'To install Py4J run: pip install py4j')

            from py4j.version import __version__
            from py4j.java_gateway import JavaGateway, GatewayParameters

            # the address and port to use to host the py4j.GatewayServer
            address = '127.0.0.1'
            port = utils.get_available_port()

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
                        raise IOError('Cannot find {0}\nCreate a PY4J_JAR environment '
                                      'variable to be equal to the full path to {0}'.format(filename))

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
                # start the py4j.GatewayServer, cannot use subprocess.call() because it blocks
                subprocess.Popen(cmd, stderr=sys.stderr, stdout=sys.stdout)
                err = None
            except IOError:
                err = 'You must have a Java Runtime Environment installed and available on PATH'

            if err:
                raise IOError(err)

            utils.wait_for_server(address, port, 5.0)

            self._gateway = JavaGateway(
                gateway_parameters=GatewayParameters(address=address, port=port)
            )

            self._lib = self._gateway.jvm

        elif libtype == 'net':
            if not utils.is_pythonnet_installed():
                raise IOError('Cannot load a .NET Assembly because pythonnet is not installed.\n'
                              'To install pythonnet run: pip install pythonnet')

            import clr
            try:
                # By default, pythonnet can only load libraries that are for .NET 4.0+.
                #
                # In order to allow pythonnet to load a library from .NET <4.0 the
                # useLegacyV2RuntimeActivationPolicy property needs to be enabled
                # in a <python-executable>.config file. If the following statement
                # raises a FileLoadException then attempt to create the configuration
                # file that has the property enabled and then notify the user why
                # loading the library failed and ask them to re-run their Python
                # script to load the .NET library.
                self._assembly = clr.System.Reflection.Assembly.LoadFile(self._path)

            except clr.System.IO.FileLoadException as err:
                # Example error message that can occur if the library is for .NET <4.0,
                # and the useLegacyV2RuntimeActivationPolicy is not enabled:
                #
                # " Mixed mode assembly is built against version 'v2.0.50727' of the
                #  runtime and cannot be loaded in the 4.0 runtime without additional
                #  configuration information. "
                if str(err).startswith('Mixed mode assembly'):
                    status, msg = utils.check_dot_net_config(sys.executable)
                    if not status == 0:
                        raise IOError(msg)
                    else:
                        update_msg = 'Checking .NET config returned "{}" '.format(msg)
                        update_msg += 'and still cannot load library.\n'
                        update_msg += str(err)
                        raise IOError(update_msg)
                raise IOError('The above "System.IO.FileLoadException" is not handled.\n')

            # the shared library must be available in sys.path
            head, tail = os.path.split(self._path)
            sys.path.append(head)

            # don't include the library extension
            clr.AddReference(os.path.splitext(tail)[0])

            # import namespaces, create instances of classes or reference a System.Type[] object
            dotnet = dict()
            for t in self._assembly.GetTypes():
                if t.Namespace is not None:
                    mod = __import__(t.Namespace)
                    if mod.__name__ not in dotnet:
                        dotnet[mod.__name__] = mod
                else:
                    try:
                        dotnet[t.Name] = self._assembly.CreateInstance(t.FullName)
                    except:
                        if t.Name not in dotnet:
                            dotnet[t.Name] = t
            self._lib = DotNet(dotnet, self._path)

        else:
            raise TypeError('Cannot load libtype={}'.format(libtype))
        logger.debug('Loaded ' + self._path)

    def __repr__(self):
        return '<{} id={:#x} libtype={} path={}>'.format(
            self.__class__.__name__, id(self), self._lib.__class__.__name__, self._path)

    def __del__(self):
        if self._gateway is not None:
            self._gateway.shutdown()
            logger.debug('shutdown py4j.GatewayServer')

    @property
    def assembly(self):
        """
        Returns a reference to the `.NET Runtime Assembly <NET_>`_ object, *only if
        the shared library is a .NET Framework*, otherwise returns :obj:`None`.

        .. tip::
           The `JetBrains dotPeek`_ program can be used to reliably decompile any
           .NET Assembly in to the equivalent source code.

        .. _NET: https://msdn.microsoft.com/en-us/library/system.reflection.assembly(v=vs.110).aspx
        .. _JetBrains dotPeek: https://www.jetbrains.com/decompiler/
        """
        return self._assembly

    @property
    def gateway(self):
        """
        Returns the :class:`~py4j.java_gateway.JavaGateway` object, *only if
        the shared library is a Java archive*, otherwise returns :obj:`None`.
        """
        return self._gateway

    @property
    def lib(self):
        """Returns the reference to the loaded library object.

        For example, if `libtype` is

            * ``'cdll'`` then a :class:`~ctypes.CDLL` object
            * ``'windll'`` then a :class:`~ctypes.WinDLL` object
            * ``'oledll'`` then a :class:`~ctypes.OleDLL` object
            * ``'net'`` then a :class:`~.load_library.DotNet` object
            * ``'java'`` then a :class:`~py4j.java_gateway.JVMView` object
        """
        return self._lib

    @property
    def path(self):
        """:class:`str`: The path to the shared library file."""
        return self._path


class DotNet(object):

    def __init__(self, dot_net_dict, path):
        """Contains the namespace_ modules, classes and `System.Type`_ objects of a .NET Assembly.

        Do not instantiate directly.

        .. _namespace: https://msdn.microsoft.com/en-us/library/z2kcy19k.aspx
        .. _System.Type: https://msdn.microsoft.com/en-us/library/system.type(v=vs.110).aspx
        """
        self.__dict__.update(dot_net_dict)
        self._path = path

    def __repr__(self):
        return '<{} id={:#x} path={}>'.format(
            self.__class__.__name__, id(self), self._path)
