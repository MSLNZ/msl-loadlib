"""
Common functions used by the **MSL-LoadLib** package.
"""
import os
import time
import socket
import logging
import subprocess
import xml.etree.ElementTree as ET
try:
    import winreg
except ImportError:
    try:
        import _winreg as winreg  # Python 2 on Windows
    except ImportError:
        winreg = None  # not Windows

from .exceptions import ConnectionTimeoutError
from . import IS_MAC

logger = logging.getLogger(__package__)


NET_FRAMEWORK_DESCRIPTION = """
<!--
  Created by the MSL-LoadLib package.

  By default, applications that target the .NET Framework version 4.0+ cannot load assemblies from
  previous .NET Framework versions. You must add and modify the "app".config file and set the
  useLegacyV2RuntimeActivationPolicy property to be "true". For the Python executable this would be
  a python.exe.config (Windows) or python.config (Unix) configuration file.

  For example, Python for .NET (pythonnet, https://pythonnet.github.io/) only works with .NET 4.0+
  and therefore it cannot automatically load a shared library that was compiled with .NET <4.0. If
  you try to load the library and a System.IO.FileNotFoundException is raised then that might
  mean that the library is from .NET <4.0.

  Additionally, the System.IO.FileNotFoundException exception will also be raised if the folder
  that the DLL is located in is not within sys.path, so first make sure that the shared library
  is visible to the Python interpreter.

  See https://support.microsoft.com/kb/2572158 for an overview.

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


def is_pythonnet_installed():
    """Checks if `Python for .NET`_ is installed.

    .. _Python for .NET: https://pythonnet.github.io/

    Returns
    -------
    :class:`bool`
        Whether `Python for .NET`_ is installed.

    Note
    ----
    For help getting `Python for .NET`_ installed on a non-Windows operating system look at
    the :ref:`prerequisites <loadlib-prerequisites>`, the `Mono <https://www.mono-project.com/>`_
    project and the `Python for .NET documentation <Python for .NET_>`_.
    """
    try:
        import clr
    except ImportError:
        logger.warning('Python for .NET <pythonnet> is not installed. Cannot load a .NET library.')
        return False
    return True


def is_py4j_installed():
    """Checks if Py4J_ is installed.

    .. versionadded:: 0.4

    .. _Py4J: https://www.py4j.org/index.html#

    Returns
    -------
    :class:`bool`
        Whether Py4J_ is installed.
    """
    try:
        import py4j
    except ImportError:
        logger.warning('Py4j is not installed. Cannot load a JAVA archive or class file.')
        return False
    return True


def is_comtypes_installed():
    """Checks if comtypes_ is installed.

    .. versionadded:: 0.5

    .. _comtypes: https://pythonhosted.org/comtypes/#

    Returns
    -------
    :class:`bool`
        Whether comtypes_ is installed.
    """
    try:
        import comtypes
    except ImportError:
        logger.warning('comtypes is not installed. Cannot load a COM library.')
        return False
    return True


def check_dot_net_config(py_exe_path):
    """Check if the **useLegacyV2RuntimeActivationPolicy** property is enabled.

    By default, `Python for .NET <https://pythonnet.github.io/>`_ only works with .NET
    4.0+ and therefore it cannot automatically load a shared library that was compiled
    with .NET <4.0. This method ensures that the **useLegacyV2RuntimeActivationPolicy**
    property exists in the **<python-executable>.config** file and that it is enabled.

    This `link <https://stackoverflow.com/questions/14508627/>`_ provides an overview
    explaining why the **useLegacyV2RuntimeActivationPolicy** property is required.

    The **<python-executable>.config** file should look like

    .. code-block:: xml

        <?xml version ="1.0"?>
        <configuration>
            <startup useLegacyV2RuntimeActivationPolicy="true">
                <supportedRuntime version="v4.0" />
                <supportedRuntime version="v2.0.50727" />
            </startup>
        </configuration>

    Parameters
    ----------
    py_exe_path : :class:`str`
        The path to the Python executable.

    Returns
    -------
    :class:`int`
        One of the following values:

            * -1 -- if there was a problem
            * 0 -- if the .NET property was already enabled, or
            * 1 -- if the property was created successfully.

    :class:`str`
        A message describing the outcome.
    """

    config_path = py_exe_path + '.config'

    if os.path.isfile(config_path):

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
            with open(config_path, 'r') as fp:
                lines = fp.readlines()

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


def is_port_in_use(port):
    """Checks whether the network port is in use.

    .. versionchanged:: 0.7.0
       Renamed from `port_in_use` and added support for macOS.

    Parameters
    ----------
    port : :class:`int`
        The port number to test.

    Returns
    -------
    :class:`bool`
        Whether the port is in use.
    """
    if IS_MAC:
        cmd = ['lsof', '-nPw', '-iTCP']
    else:
        cmd = ['netstat', '-an']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        raise RuntimeError(err.decode(errors='ignore'))
    return out.find(b':%d ' % port) > 0


def get_available_port():
    """:class:`int`: Returns a port number that is available."""
    sock = socket.socket()
    sock.bind(('', 0))  # get any available port
    port = sock.getsockname()[1]
    sock.close()
    return port


def wait_for_server(host, port, timeout):
    """Wait for the 32-bit server to start.

    Parameters
    ----------
    host : :class:`str`
        The host address of the server, e.g., ``'127.0.0.1'``.
    port : :class:`int`
        The port number of the server.
    timeout : :class:`float`
        The maximum number of seconds to wait to establish a connection to the server.

    Raises
    ------
    ~msl.loadlib.exceptions.ConnectionTimeoutError
        If a timeout occurred.
    """

    # wait for the server to be running -- essentially this is the subprocess.wait() method
    stop = time.time() + max(0.0, timeout)
    while True:
        if is_port_in_use(port):
            break
        if time.time() > stop:
            raise ConnectionTimeoutError(
                'Timeout after {:.1f} seconds. Could not connect to {}:{}'.format(timeout, host, port)
            )


def get_com_info(*additional_keys):
    """Reads the registry for the COM_ libraries that are available.

    This function is only supported on Windows.

    .. versionadded:: 0.5

    .. _COM: https://en.wikipedia.org/wiki/Component_Object_Model
    .. _Class ID: https://docs.microsoft.com/en-us/windows/desktop/com/clsid-key-hklm

    Parameters
    ----------
    *additional_keys : :class:`str`, optional
        The Program ID (ProgID) key is returned automatically. You can include
        additional keys (e.g., Version, InprocHandler32, ToolboxBitmap32,
        VersionIndependentProgID, ...) if you also want this additional
        information to be returned for each `Class ID`_.

    Returns
    -------
    :class:`dict`
        The keys are the Class ID's and each value is a :class:`dict`
        of the information that was requested.

    Examples
    --------
    >>> from msl.loadlib import utils
    >>> info = utils.get_com_info()
    >>> info = utils.get_com_info('Version', 'ToolboxBitmap32')
    """
    if winreg is None:
        return {}

    results = {}
    for item in ['CLSID', r'Wow6432Node\CLSID']:
        try:
            key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, item)
        except OSError:
            continue
        else:
            logger.debug(r'Parsing HKEY_CLASSES_ROOT\{}\...'.format(item))

        index = -1
        while True:
            index += 1
            try:
                clsid = winreg.EnumKey(key, index)
            except OSError:
                break

            sub_key = winreg.OpenKey(key, clsid)

            # ProgID is mandatory, if this fails then ignore
            # this CLSID and go to the next index in the registry
            try:
                progid = winreg.QueryValue(sub_key, 'ProgID')
            except OSError:
                pass
            else:
                results[clsid] = {}
                results[clsid]['ProgID'] = progid

                for name in additional_keys:
                    try:
                        results[clsid][name] = winreg.QueryValue(sub_key, name)
                    except OSError:
                        results[clsid][name] = None
            finally:
                winreg.CloseKey(sub_key)

        winreg.CloseKey(key)

    return results
