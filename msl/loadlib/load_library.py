"""
Load a :class:`~ctypes.CDLL`, :class:`~ctypes.WinDLL`, :class:`~ctypes.OleDLL`, or
a `.NET Framework <http://pythonnet.github.io/>`_ library.
"""
import os
import sys
import ctypes
import ctypes.util
import logging
import xml.etree.ElementTree as ET

from msl.loadlib import DEFAULT_EXTENSION

logger = logging.getLogger(__name__)


class LoadLibrary(object):

    def __init__(self, path, libtype='cdll', get_assembly_types=True):
        """Load a shared library.

        Based on the value of `libtype` this class will load the shared library as a:

            * :class:`~ctypes.CDLL` if `libtype` = ``'cdll'``,
            * :class:`~ctypes.WinDLL` if `libtype` = ``'windll'``,
            * :class:`~ctypes.OleDLL` if `libtype` = ``'oledll'``, or a
            * :class:`~.load_library.DotNetContainer` if `libtype` = ``'net'`` **and**
              `get_assembly_types` = :obj:`True`.

        Parameters
        ----------
        path : :obj:`str`
            The path to the shared library.

            The search order for finding the shared library is:

                1. assume that a full or a relative (to the current working directory)
                   path is specified,
                2. use :obj:`ctypes.util.find_library` to find the shared library file,
                3. search :obj:`sys.path`, then
                4. search :obj:`os.environ['PATH'] <os.environ>` to find the shared library.

        libtype : :obj:`str`, optional
            The library type to use for the calling convention.

            The following values are allowed:

            * ``'cdll'``, for a __cdecl library
            * ``'windll'`` or ``'oledll'``, for a __stdcall library (Windows only)
            * ``'net'``, for a .NET library

            Default is ``'cdll'``.

        get_assembly_types : :obj:`bool`, optional
            Whether to automatically call
            `System.Reflection.Assembly.GetTypes <https://msdn.microsoft.com/en-us/library/system.reflection.assembly.gettypes(v=vs.110).aspx>`_
            when a .NET library is loaded to parse the types in the assembly. This
            parameter is only used if `libtype` = ``'net'``. If this value is
            :obj:`False` then the :obj:`lib` property value will return :obj:`None`,
            but you can still import .NET modules and access the attributes of
            the :obj:`assembly`.

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

        # create a new reference to `path` just in case the
        # DEFAULT_EXTENSION is appended below so that the
        # ctypes.util.find_library function call will use the
        # unmodified value of `path`
        _path = path

        # assume a default extension if no extension was provided
        if not os.path.splitext(_path)[1]:
            _path += DEFAULT_EXTENSION

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

        if libtype == 'cdll':
            self._lib = ctypes.CDLL(self._path)
        elif libtype == 'windll':
            self._lib = ctypes.WinDLL(self._path)
        elif libtype == 'oledll':
            self._lib = ctypes.OleDLL(self._path)
        elif libtype == 'net' and self.is_pythonnet_installed():
            import clr
            try:
                # By default, pythonnet can only load libraries that are for .NET 4.0+.
                #
                # In order to allow pythonnet to load a library from .NET <4.0 the
                # useLegacyV2RuntimeActivationPolicy property needs to be enabled
                # in a python.exe.config file. If the following statement raises a
                # FileLoadException then attempt to create the configuration file
                # that has the property enabled and then notify the user why
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
                #
                # To solve this problem, a <python-executable>.config file must exist
                # and it must contain a useLegacyV2RuntimeActivationPolicy property
                # that is set to be "true".
                if "Mixed mode assembly" in str(err):
                    status, msg = self.check_dot_net_config(sys.executable)
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

            if get_assembly_types:
                # import namespaces, create instances of classes or reference a System.Type[] object
                dotnet = dict()
                for t in self._assembly.GetTypes():
                    if t.Namespace is not None:
                        if t.Namespace not in dotnet:
                            dotnet[t.Namespace] = __import__(t.Namespace)
                    else:
                        try:
                            dotnet[t.Name] = self._assembly.CreateInstance(t.FullName)
                        except:
                            if t.Name not in dotnet:
                                dotnet[t.Name] = t
                self._lib = DotNetContainer(dotnet)

        else:
            raise TypeError('Cannot load libtype={}'.format(libtype))
        logger.debug('Loaded ' + self._path)

    def __repr__(self):
        return '<{} id={:#x} libtype={} path={}>'.format(
            self.__class__.__name__, id(self), self._lib.__class__.__name__, self._path)

    @property
    def assembly(self):
        """
        Returns the reference to the `.NET Runtime Assembly <NET_>`_ object, *only if
        the shared library is a .NET library*, otherwise returns :obj:`None`.

        .. tip::
           The `JetBrains dotPeek <https://www.jetbrains.com/decompiler/>`_ program can be used
           to reliably decompile any .NET assembly into the equivalent C# source code.

        .. _NET: https://msdn.microsoft.com/en-us/library/system.reflection.assembly(v=vs.110).aspx
        """
        return self._assembly

    @property
    def lib(self):
        """Returns the reference to the loaded library object.

        For example:

            * if `libtype` = ``'cdll'`` then a :class:`~ctypes.CDLL` object is returned
            * if `libtype` = ``'windll'`` then a :class:`~ctypes.WinDLL` object is returned
            * if `libtype` = ``'oledll'`` then a :class:`~ctypes.OleDLL` object is returned
            * if `libtype` = ``'net'`` **and** the :class:`LoadLibrary` class was instantiated
              with `get_assembly_types` = :obj:`True` then a :class:`~.load_library.DotNetContainer`
              object is returned, which contains the types defined in the .NET assembly
              (i.e., the namespace_ modules, classes and/or System.Type_ objects). If
              `get_assembly_types` = :obj:`False` then :obj:`None` is returned; however,
              you can still access the .NET :obj:`assembly` object and import the .NET modules.

        .. _namespace: https://msdn.microsoft.com/en-us/library/z2kcy19k.aspx
        .. _System.Type: https://msdn.microsoft.com/en-us/library/system.type(v=vs.110).aspx
        """
        return self._lib

    @property
    def path(self):
        """:obj:`str`: The path to the shared library file."""
        return self._path

    @staticmethod
    def is_pythonnet_installed():
        """Checks if `Python for .NET <http://pythonnet.github.io/>`_ is installed.

        Returns
        -------
        :obj:`bool`
            Whether Python for .NET is installed.

        Note
        ----
        For help getting Python for .NET working on a non-Windows operating system look at
        the :ref:`prerequisites`, the `Mono <http://www.mono-project.com/>`_ project and
        the `Python for .NET documentation <http://pythonnet.sourceforge.net/readme.html>`_.
        """
        try:
            import clr
        except ImportError:
            logger.warning('Python for .NET <pythonnet> is not installed. Cannot load a .NET library.')
            return False
        return True

    @staticmethod
    def check_dot_net_config(py_exe_path):
        """Check if the **useLegacyV2RuntimeActivationPolicy** property is enabled.

        By default, `Python for .NET <http://pythonnet.github.io/>`_ only works with .NET
        4.0+ and therefore it cannot automatically load a shared library that was compiled
        with .NET <4.0. This method ensures that the **useLegacyV2RuntimeActivationPolicy**
        property exists in the **<python-executable>.config** file and that it is enabled.

        This `link <http://stackoverflow.com/questions/14508627/>`_ provides an overview
        explaining why the **useLegacyV2RuntimeActivationPolicy** property is required.

        The **<python-executable>.config** file should look like::

            <?xml version ="1.0"?>
            <configuration>
                <startup useLegacyV2RuntimeActivationPolicy="true">
                    <supportedRuntime version="v4.0" />
                    <supportedRuntime version="v2.0.50727" />
                </startup>
            </configuration>

        Parameters
        ----------
        py_exe_path : :obj:`str`
            The path to the Python executable.

        Returns
        -------
        :obj:`int`
            One of the following values:
            
                * -1 -- if there was a problem
                * 0 -- if the .NET property was already enabled, or
                * 1 -- if the property was created successfully.

        :obj:`str`
            A message describing the outcome.
        """

        config_path = py_exe_path + '.config'

        if os.path.isfile(config_path):

            with open(config_path, 'r') as fp:
                lines = fp.readlines()

            # use the ElementTree to parse the file
            try:
                tree = ET.parse(config_path)
            except ET.ParseError:
                msg = 'Invalid XML file ' + config_path
                msg += '\nCannot create useLegacyV2RuntimeActivationPolicy property.'
                logger.warning(msg)
                return -1, msg

            root = tree.getroot()

            if not root.tag == 'configuration':
                msg = 'The root tag in {} is "{}".\n'.format(config_path, root.tag)
                msg += 'It must be "configuration" in order to create a .NET Framework config file '
                msg += 'to enable the useLegacyV2RuntimeActivationPolicy property.\n'
                msg += 'To load an assembly from a .NET Framework version < 4.0 the '
                msg += 'following must be in {}:\n'.format(config_path)
                msg += '<configuration>' + NET_FRAMEWORK_FIX + '</configuration>\n'
                logger.warning(msg)
                return -1, msg

            # check if the policy exists
            policy = root.find('startup/[@useLegacyV2RuntimeActivationPolicy]')
            if policy is None:
                lines.insert(-1, NET_FRAMEWORK_FIX)
                with open(config_path, 'w') as fp:
                    fp.writelines(lines)
                msg = 'Added the useLegacyV2RuntimeActivationPolicy property to ' + config_path
                msg += '\nTry again to see if Python can now load the .NET library.\n'
                return 1, msg
            else:
                if not policy.attrib['useLegacyV2RuntimeActivationPolicy'].lower() == 'true':
                    msg = 'The useLegacyV2RuntimeActivationPolicy in {} is False\n'.format(config_path)
                    msg += 'Cannot load an assembly from a .NET Framework version < 4.0.'
                    logger.warning(msg)
                    return -1, msg
                return 0, 'The useLegacyV2RuntimeActivationPolicy property is enabled'

        else:
            with open(config_path, 'w') as f:
                f.write('<?xml version ="1.0"?>')
                f.write(NET_FRAMEWORK_DESCRIPTION)
                f.write('<configuration>')
                f.write(NET_FRAMEWORK_FIX)
                f.write('</configuration>\n')
            msg = 'The library appears to be from a .NET Framework version < 4.0.\n'
            msg += 'The useLegacyV2RuntimeActivationPolicy property was added to {}\n'.format(config_path)
            msg += 'to fix the "System.IO.FileLoadException: Mixed mode assembly..." error.\n'
            msg += 'Rerun the script, or shutdown and restart the interactive console, to see\n'
            msg += 'if Python can now load the .NET library.\n'
            return 1, msg


class DotNetContainer(object):
    """A container for the namespace_ modules, classes and `System.Type`_ objects
    of a .NET library.

    .. _namespace: https://msdn.microsoft.com/en-us/library/z2kcy19k.aspx
    .. _System.Type: https://msdn.microsoft.com/en-us/library/system.type(v=vs.110).aspx
    """
    def __init__(self, dotnet_dict):
        self.__dict__.update(dotnet_dict)


NET_FRAMEWORK_DESCRIPTION = """
<!--
  Created by the MSL-LoadLib package.

  By default, applications that target the .NET Framework version 4.0+ cannot load assemblies from
  previous .NET Framework versions. You must add and modify the "app".config file and set the
  useLegacyV2RuntimeActivationPolicy property to be "true". For the Python executable this would be
  a python.exe.config (Windows) or python.config (Unix) configuration file.

  For example, Python for .NET (pythonnet, http://pythonnet.github.io/) only works with .NET 4.0+
  and therefore it cannot automatically load a shared library that was compiled with .NET <4.0. If
  you try to load the library and a System.IO.FileNotFoundException is raised then that might
  mean that the library is from .NET <4.0.

  Additionally, the System.IO.FileNotFoundException exception will also be raised if the folder
  that the DLL is located in is not within sys.path, so first make sure that the shared library
  is visible to the Python interpreter.

  See http://support.microsoft.com/kb/2572158 for an overview.

  NOTE: To install pythonnet, run:
  $ pip install pythonnet
-->
"""

NET_FRAMEWORK_FIX = """
    <startup useLegacyV2RuntimeActivationPolicy="true">
        <supportedRuntime version="v4.0" />
        <supportedRuntime version="v2.0.50727" />
    </startup>
"""
