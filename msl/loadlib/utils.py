"""
Common functions used by the **MSL-LoadLib** package.
"""
import logging
import os
import socket
import subprocess
import time
import xml.etree.ElementTree as ET
try:
    import winreg
except ImportError:
    try:
        import _winreg as winreg  # Python 2 on Windows
    except ImportError:
        winreg = None  # not Windows

from . import IS_LINUX
from . import IS_WINDOWS
from .exceptions import ConnectionTimeoutError

logger = logging.getLogger(__package__)


NET_FRAMEWORK_DESCRIPTION = """
<!--
  Created by the MSL-LoadLib package.

  By default, applications that target the .NET Framework version 4.0+ cannot load
  assemblies from previous .NET Framework versions. You must add and modify the
  <app>.config file and set the useLegacyV2RuntimeActivationPolicy property to be
  "true". For the Python executable this would be a python.exe.config (Windows) 
  or python.config (Linux) configuration file.

  Python for .NET (https://pythonnet.github.io/) works with .NET 4.0+ and 
  therefore it cannot automatically load a shared library that was compiled with
  .NET < 4.0. If you try to load the library and a System.IO.FileLoadException is
  raised then that might mean that the library is from .NET < 4.0.

  The System.IO.FileLoadException exception could also be raised if the directory
  that the DLL is located in, or a dependency of the library, is not within PATH. 

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
        return False
    return True


def check_dot_net_config(py_exe_path):
    """Check if the **useLegacyV2RuntimeActivationPolicy** property is enabled.

    By default, `Python for .NET <https://pythonnet.github.io/>`_ works with .NET
    4.0+ and therefore it cannot automatically load a shared library that was compiled
    with .NET <4.0. This method ensures that the **useLegacyV2RuntimeActivationPolicy**
    property exists in the **<python-executable>.config** file and that it is enabled.

    This `link <https://stackoverflow.com/questions/14508627/>`_ provides an overview
    explaining why the **useLegacyV2RuntimeActivationPolicy** property is required.

    The **<python-executable>.config** file should look like

    .. code-block:: xml

        <?xml version="1.0" encoding="utf-8" ?>
        <configuration>
            <startup useLegacyV2RuntimeActivationPolicy="true">
                <supportedRuntime version="v4.0" />
                <supportedRuntime version="v2.0.50727" />
            </startup>
        </configuration>

    Parameters
    ----------
    py_exe_path : :class:`str`
        The path to a Python executable.

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
            msg = 'Invalid XML file {}\n' \
                  'Cannot create the useLegacyV2RuntimeActivationPolicy ' \
                  'property.\n'.format(config_path)
            logger.warning(msg)
            return -1, msg

        root = tree.getroot()

        if root.tag != 'configuration':
            msg = 'The root tag in {config_path} is <{tag}>.\n' \
                  'It must be <configuration> in order to create a .NET Framework config\n' \
                  'file which enables the useLegacyV2RuntimeActivationPolicy property.\n' \
                  'To load an assembly from a .NET Framework version < 4.0 the following\n' \
                  'must be in {config_path}\n\n' \
                  '<configuration>{fix}</configuration>\n'.format(
                   config_path=config_path, tag=root.tag, fix=NET_FRAMEWORK_FIX)
            logger.warning(msg)
            return -1, msg

        # check if the policy exists
        policy = root.find('startup/[@useLegacyV2RuntimeActivationPolicy]')
        if policy is None:
            with open(config_path, mode='rt') as fp:
                lines = fp.readlines()

            lines.insert(-1, NET_FRAMEWORK_FIX)
            with open(config_path, mode='wt') as fp:
                fp.writelines(lines)
            msg = 'Added the useLegacyV2RuntimeActivationPolicy property to\n' \
                  '{config_path}\n' \
                  'Try again to see if Python can now load the .NET library.\n'.format(
                   config_path=config_path)
            return 1, msg
        else:
            if not policy.attrib['useLegacyV2RuntimeActivationPolicy'].lower() == 'true':
                msg = 'The useLegacyV2RuntimeActivationPolicy in\n' \
                      '{config_path}\n' \
                      'is "false". Cannot load an assembly from a .NET Framework ' \
                      'version < 4.0.\n'.format(config_path=config_path)
                logger.warning(msg)
                return -1, msg
            return 0, 'The useLegacyV2RuntimeActivationPolicy property is enabled'

    else:
        with open(config_path, mode='wt') as f:
            f.write('<?xml version="1.0" encoding="utf-8" ?>')
            f.write(NET_FRAMEWORK_DESCRIPTION)
            f.write('<configuration>')
            f.write(NET_FRAMEWORK_FIX)
            f.write('</configuration>\n')

        msg = 'The library appears to be from a .NET Framework version < 4.0.\n' \
              'The useLegacyV2RuntimeActivationPolicy property was added to\n' \
              '{config_path}\n' \
              'to fix the "System.IO.FileLoadException: Mixed mode assembly..." error.\n' \
              'Rerun the script, or restart the interactive console, to see if\n' \
              'Python can now load the .NET library.\n'.format(config_path=config_path)
        return 1, msg


def is_port_in_use(port):
    """Checks whether the TCP port is in use.

    .. versionchanged:: 0.10.0
       Only check TCP ports (instead of both TCP and UDP ports).
       Uses the ``ss`` command instead of ``netstat`` on Linux.

    .. versionchanged:: 0.7.0
       Renamed from `port_in_use` and added support for macOS.

    Parameters
    ----------
    port : :class:`int`
        The port number to test.

    Returns
    -------
    :class:`bool`
        Whether the TCP port is in use.
    """
    flags = 0
    if IS_WINDOWS:
        flags = 0x08000000  # fixes issue 31, CREATE_NO_WINDOW = 0x08000000
        cmd = ['netstat', '-a', '-n', '-p', 'TCP']
    elif IS_LINUX:
        cmd = ['ss', '-ant']
    else:
        cmd = ['lsof', '-nPw', '-iTCP']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=flags)
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
    stop = time.time() + max(0.0, timeout)
    while True:
        if is_port_in_use(port):
            return

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
            logger.debug(r'Parsing HKEY_CLASSES_ROOT\%s\...', item)

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


def generate_com_wrapper(lib, out_dir=None):
    """Generate a Python wrapper module around a COM library.

    For more information see `Accessing type libraries`_.

    .. versionadded:: 0.9

    .. _Accessing type libraries: https://pythonhosted.org/comtypes/#accessing-type-libraries

    Parameters
    ----------
    lib
        Can be any of the following

            * a :class:`~msl.loadlib.load_library.LoadLibrary` object
            * the `ProgID` or `CLSID` of a registered COM library as a :class:`str`
            * a COM pointer instance
            * an ITypeLib COM pointer instance
            * a path to a library file (.tlb, .exe or .dll) as a :class:`str`
            * a :class:`tuple` or :class:`list` specifying the GUID of a library,
              a major and a minor version number, plus optionally an LCID number,
              e.g., (guid, major, minor, lcid=0)
            * an object with ``_reg_libid_`` and ``_reg_version_`` attributes

    out_dir : :class:`str`, optional
        The output directory to save the wrapper to. If not specified then
        saves it to the ``../site-packages/comtypes/gen`` directory.

    Returns
    -------
    The wrapper module that was generated.
    """
    if not is_comtypes_installed():
        raise OSError(
            'Cannot create a COM wrapper because comtypes is not installed, run\n'
            '  pip install comtypes'
        )

    import comtypes.client

    mod = None

    # cache the value of gen_dir to reset it later
    cached_gen_dir = comtypes.client.gen_dir
    if out_dir is not None:
        gen_dir = os.path.abspath(out_dir)
        if not os.path.isdir(gen_dir):
            os.makedirs(gen_dir)
        comtypes.client.gen_dir = gen_dir

    def from_pointer(p):
        info = p.GetTypeInfo(0)
        type_lib, index = info.GetContainingTypeLib()
        return comtypes.client.GetModule(type_lib)

    try:
        mod = comtypes.client.GetModule(lib)
    except OSError:
        pass
    except (AttributeError, TypeError) as e:
        if 'LoadLibrary' in str(e):
            mod = from_pointer(lib.lib)
        elif hasattr(lib, '__com_interface__'):
            mod = from_pointer(lib)
        else:
            raise

    if not mod and isinstance(lib, str):
        obj = comtypes.client.CreateObject(lib)
        mod = from_pointer(obj)

    if out_dir is not None:
        comtypes.client.gen_dir = cached_gen_dir

    return mod
