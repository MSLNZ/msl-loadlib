"""
Common functions used by the **MSL-LoadLib** package.
"""
import os
import time
import socket
import logging
import subprocess
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


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


def is_pythonnet_installed():
    """Checks if `Python for .NET <http://pythonnet.github.io/>`_ is installed.

    Returns
    -------
    :class:`bool`
        Whether Python for .NET is installed.

    Note
    ----
    For help getting Python for .NET working on a non-Windows operating system look at
    the :ref:`prerequisites`, the `Mono <http://www.mono-project.com/>`_ project and
    the `Python for .NET documentation <http://pythonnet.github.io/>`_.
    """
    try:
        import clr
    except ImportError:
        logger.warning('Python for .NET <pythonnet> is not installed. Cannot load a .NET library.')
        return False
    return True


def is_py4j_installed():
    """Checks if Py4J_ is installed.

    .. _Py4J: https://www.py4j.org/index.html#

    Returns
    -------
    :class:`bool`
        Whether Py4J_ is installed.
    """
    try:
        import py4j
    except ImportError:
        logger.warning('Py4j is not installed. Cannot load a JAR file.')
        return False
    return True


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


def port_in_use(port):
    """Uses netstat_ to determine if the network port is in use.

    .. _netstat: http://www.computerhope.com/unix/unetstat.htm

    Parameters
    ----------
    port : :class:`int`
        The port number to test.

    Returns
    -------
    :class:`bool`
        Whether the port is in use.
    """
    p = subprocess.Popen(['netstat', '-an'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.communicate()[0].decode().find(':{} '.format(port)) > 0


def get_available_port():
    """:class:`int`: Returns a port number that is available."""
    sock = socket.socket()
    sock.bind(('', 0))  # get any available port
    port = sock.getsockname()[1]
    sock.close()
    return port


def wait_for_server(host, port, timeout):
    """Wait for the server to start.

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
    TimeoutError
        If a timeout occurred.
    """

    # wait for the server to be running -- essentially this is the subprocess.wait() method
    stop = time.time() + max(0.0, timeout)
    while True:
        if port_in_use(port):
            break
        if time.time() > stop:
            m = 'Timeout after {:.1f} seconds. Could not connect to {}:{}'.format(timeout, host, port)
            raise TimeoutError(m)
