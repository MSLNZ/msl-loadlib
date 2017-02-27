"""
Load a :class:`~ctypes.CDLL`, :class:`~ctypes.WinDLL`, :class:`~ctypes.OleDLL`, or
a `.NET Framework <http://pythonnet.github.io/>`_ library.
"""
import os
import sys
import ctypes
import logging
import xml.etree.ElementTree as ET

from msl.loadlib import IS_WINDOWS, IS_LINUX, IS_MAC

log = logging.getLogger(__name__)


class LoadLibrary(object):
    """
    Loads the shared library.

    Based on the value of ``libtype`` this class will load the shared library as a:

        * :py:class:`ctypes.CDLL` object if ``libtype`` = **'cdll'**,
        * :class:`ctypes.WinDLL` object if ``libtype`` = **'windll'**,
        * :class:`ctypes.OleDLL` object if ``libtype`` = **'oledll'**, or a
        * `CLR <http://pythonnet.github.io/>`_-type object if ``libtype`` = **'net'**.

    Args:
        path (str): The path to the shared library.

        libtype (str, optional): The library type to use for the calling convention.

            The following values are allowed:

            * ``libtype`` = **'cdll'**, for a **__cdecl** library
            * ``libtype`` = **'windll'** or **'oledll'**, for a **__stdcall** library (Windows only)
            * ``libtype`` = **'net'**, for a **.NET** library

            Default is **'cdll'**.

    Raises:
        IOError: If the shared library cannot be loaded.
        TypeError: If the value of ``libtype`` is not supported.
    """
    def __init__(self, path, libtype='cdll'):

        # a reference to the .NET Runtime Assembly
        self._assembly = None

        #  assume a default extension if no extension was provided
        if not os.path.splitext(path)[1]:
            if IS_WINDOWS:
                path += '.dll'
            elif IS_LINUX:
                path += '.so'
            elif IS_MAC:
                path += '.dylib'

        self._path = os.path.abspath(path)
        if not os.path.isfile(self._path):
            raise IOError('Cannot find the shared library ' + self._path + '\n')

        if libtype == 'cdll':
            self._lib = ctypes.CDLL(self._path)
        elif libtype == 'windll':
            self._lib = ctypes.WinDLL(self._path)
        elif libtype == 'oledll':
            self._lib = ctypes.OleDLL(self._path)
        elif libtype == 'net' and self.is_python_net_installed():
            import clr
            try:
                # By default, pythonnet can only load libraries that are for .NET 4.0+.
                #
                # When MSL-LoadLib is installed, the useLegacyV2RuntimeActivationPolicy
                # property should have been enabled automatically to allow for loading
                # assemblies from previous .NET Framework versions.
                self._assembly = clr.System.Reflection.Assembly.LoadFile(self._path)

            except clr.System.IO.FileLoadException as err:
                # Example error message that can occur if the library is for .NET <4.0,
                # and the useLegacyV2RuntimeActivationPolicy is not enabled:
                #
                # " Mixed mode assembly is built against version 'v2.0.50727' of the
                #  runtime and cannot be loaded in the 4.0 runtime without additional
                #  configuration information. "
                #
                # To solve this problem, a <python-executable>.config file must exist and it must
                # contain a useLegacyV2RuntimeActivationPolicy property that is set to be "true".
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
            sys.path.insert(0, head)

            # don't include the library extension
            clr.AddReference(os.path.splitext(tail)[0])

            # import namespaces, create instances of classes or reference a System.Type[] object
            dotnet = {}
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
        log.debug('Loaded ' + self._path)

    def __repr__(self):
        return '{} object at {}; libtype={}; path={}'.format(self.__class__.__name__,
                                                                hex(id(self)),
                                                                self.lib.__class__.__name__,
                                                                self._path)

    @property
    def path(self):
        """
        Returns:
            :py:class:`str`: The absolute path to the shared library file.
        """
        return self._path

    @property
    def lib(self):
        """
        Returns:
            The reference to the loaded-library object.

            For example:

            * if ``libtype`` = **'cdll'** then a :class:`ctypes.CDLL` object is returned
            * if ``libtype`` = **'windll'** then a :class:`ctypes.WinDLL` object is returned
            * if ``libtype`` = **'oledll'** then a :class:`ctypes.OleDLL` object is returned
            * if ``libtype`` = **'net'** then a :class:`~.load_library.DotNetContainer` containing
              the .NET namespaces_, classes and/or `System.Type`_ objects.

        .. _namespaces: https://msdn.microsoft.com/en-us/library/z2kcy19k.aspx
        .. _System.Type: https://msdn.microsoft.com/en-us/library/system.type(v=vs.110).aspx
        """
        return self._lib

    @property
    def assembly(self):
        """
        Returns:
            The reference to the `.NET RuntimeAssembly
            <https://msdn.microsoft.com/en-us/library/system.reflection.assembly(v=vs.110).aspx>`_
            object -- *only if the shared library is a .NET library, otherwise returns*
            :py:data:`None`.
        """
        return self._assembly

    @staticmethod
    def is_python_net_installed():
        """
        Checks if `Python for .NET <http://pythonnet.github.io/>`_ is installed.

        Returns:
            :py:class:`bool`: :py:data:`True` if it is installed.

        .. note::
           For help getting Python for .NET working on a non-Windows operating system look at
           the `Mono <http://www.mono-project.com/>`_ project and
           `here <http://pythonnet.sourceforge.net/readme.html>`_.
        """
        try:
            import clr
        except ImportError:
            log.warning('Python for .NET <pythonnet> is not installed. Cannot load a .NET library.')
            return False
        return True

    @staticmethod
    def check_dot_net_config(py_exe_path):
        """
        Check if the **useLegacyV2RuntimeActivationPolicy** property is enabled.

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

        Args:
            py_exe_path (str): The path to the Python executable.

        Returns:
            :py:class:`tuple`: (:py:class:`int`, :py:class:`str`)
            Where the first index is one of the following status values:

            * -1 if there was a problem
            * 0 if the .NET property was already enabled, or
            * 1 if the property was created successfully.

            and the second index is a message describing the outcome.
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
                log.warning(msg)
                return -1, msg

            root = tree.getroot()

            if not root.tag == 'configuration':
                msg = 'The root tag in {} is "{}".\n'.format(config_path, root.tag)
                msg += 'It must be "configuration" in order to create a .NET Framework config file '
                msg += 'to enable the useLegacyV2RuntimeActivationPolicy property.\n'
                msg += 'To load an assembly from a .NET Framework version <4.0 the '
                msg += 'following must be in {}:\n'.format(config_path)
                msg += '<configuration>' + NET_FRAMEWORK_FIX + '</configuration>\n'
                log.warning(msg)
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
                    msg += 'Cannot load an assembly from a .NET Framework version <4.0.'
                    log.warning(msg)
                    return -1, msg
                return 0, 'The useLegacyV2RuntimeActivationPolicy property is enabled'

        else:
            with open(config_path, 'w') as f:
                f.write('<?xml version ="1.0"?>')
                f.write(NET_FRAMEWORK_DESCRIPTION)
                f.write('<configuration>')
                f.write(NET_FRAMEWORK_FIX)
                f.write('</configuration>\n')
            msg = 'Added the useLegacyV2RuntimeActivationPolicy property to ' + config_path
            msg += '\nto fix the "System.IO.FileLoadException: Mixed mode assembly..." error.\n'
            msg += 'Try again to see if Python can now load the .NET library.\n'
            return 1, msg


class DotNetContainer(object):
    """
    A container for the namespace_ modules, classes and `System.Type`_ objects
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
