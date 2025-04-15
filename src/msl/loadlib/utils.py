"""
Common functions used by the **MSL-LoadLib** package.
"""

from __future__ import annotations

import logging
import os
import socket
import subprocess
import time
from types import ModuleType
from typing import Any
from xml.etree import ElementTree

try:
    import winreg
except ImportError:
    winreg = None  # not Windows

from .constants import IS_LINUX
from .constants import IS_WINDOWS
from .constants import NET_FRAMEWORK_FIX
from .constants import NET_FRAMEWORK_DESCRIPTION
from .exceptions import ConnectionTimeoutError

logger = logging.getLogger(__package__)


def is_pythonnet_installed() -> bool:
    """Checks if `Python for .NET`_ is installed.

    .. _Python for .NET: https://pythonnet.github.io/

    :return: Whether `Python for .NET`_ is installed.

    .. note::
        For help getting `Python for .NET`_ installed on a non-Windows operating system look at
        the :ref:`prerequisites <loadlib-prerequisites>`, the `Mono <https://www.mono-project.com/>`_
        project and the `Python for .NET documentation <Python for .NET_>`_.
    """
    try:
        import clr
    except ImportError:
        return False
    return True


def is_py4j_installed() -> bool:
    """Checks if Py4J_ is installed.

    .. versionadded:: 0.4

    .. _Py4J: https://www.py4j.org/index.html#

    :return: Whether Py4J_ is installed.
    """
    try:
        import py4j
    except ImportError:
        return False
    return True


def is_comtypes_installed() -> bool:
    """Checks if comtypes_ is installed.

    .. versionadded:: 0.5

    .. _comtypes: https://pythonhosted.org/comtypes/#

    :return: Whether comtypes_ is installed.
    """
    try:
        import comtypes
    except ImportError:
        return False
    return True


def check_dot_net_config(py_exe_path: str) -> tuple[int, str]:
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

    :param py_exe_path: The path to a Python executable.
    :return: A status flag and a message describing the outcome.

        The flag will be one of the following values:

            * -1: if there was a problem
            * 0: if the .NET property was already enabled, or
            * 1: if the property was created successfully.
    """
    config_path = f"{py_exe_path}.config"

    if os.path.isfile(config_path):
        try:
            tree = ElementTree.parse(config_path)
        except ElementTree.ParseError:
            msg = f"Invalid XML file {config_path}\nCannot create the useLegacyV2RuntimeActivationPolicy property.\n"
            logger.warning(msg)
            return -1, msg

        root = tree.getroot()

        if root.tag != "configuration":
            msg = (
                f"The root tag in {config_path} is <{root.tag}>.\n"
                f"It must be <configuration> in order to create a .NET Framework config\n"
                f"file which enables the useLegacyV2RuntimeActivationPolicy property.\n"
                f"To load an assembly from a .NET Framework version < 4.0 the following\n"
                f"must be in {config_path}\n\n"
                f"<configuration>{NET_FRAMEWORK_FIX}</configuration>\n"
            )
            logger.warning(msg)
            return -1, msg

        # check if the policy exists
        policy = root.find("startup/[@useLegacyV2RuntimeActivationPolicy]")
        if policy is None:
            with open(config_path, mode="rt") as fp:
                lines = fp.readlines()

            lines.insert(-1, NET_FRAMEWORK_FIX)
            with open(config_path, mode="wt") as fp:
                fp.writelines(lines)
            msg = (
                f"Added the useLegacyV2RuntimeActivationPolicy property to\n"
                f"{config_path}\n"
                f"Try again to see if Python can now load the .NET library.\n"
            )
            return 1, msg
        else:
            if not policy.attrib["useLegacyV2RuntimeActivationPolicy"].lower() == "true":
                msg = (
                    f"The useLegacyV2RuntimeActivationPolicy in\n{config_path}\n"
                    f'is "false". Cannot load an assembly from a .NET Framework '
                    f"version < 4.0.\n"
                )
                logger.warning(msg)
                return -1, msg
            return 0, "The useLegacyV2RuntimeActivationPolicy property is enabled"

    else:
        with open(config_path, mode="wt") as f:
            f.write('<?xml version="1.0" encoding="utf-8" ?>')
            f.write(NET_FRAMEWORK_DESCRIPTION)
            f.write("<configuration>")
            f.write(NET_FRAMEWORK_FIX)
            f.write("</configuration>\n")

        msg = (
            f"The library appears to be from a .NET Framework version < 4.0.\n"
            f"The useLegacyV2RuntimeActivationPolicy property was added to\n"
            f"{config_path}\n"
            f'to fix the "System.IO.FileLoadException: Mixed mode assembly..." error.\n'
            f"Rerun the script, or restart the interactive console, to see if\n"
            f"Python can now load the .NET library.\n"
        )
        return 1, msg


def is_port_in_use(port: int) -> bool:
    """Checks whether the TCP port is in use.

    .. versionchanged:: 0.10.0
       Only check TCP ports (instead of both TCP and UDP ports).
       Uses the ``ss`` command instead of ``netstat`` on Linux.

    .. versionchanged:: 0.7.0
       Renamed from `port_in_use` and added support for macOS.

    :param port: The port number to test.
    :return: Whether the TCP port is in use.
    """
    flags = 0
    if IS_WINDOWS:
        flags = 0x08000000  # fixes issue 31, CREATE_NO_WINDOW = 0x08000000
        cmd = ["netstat", "-a", "-n", "-p", "TCP"]
    elif IS_LINUX:
        cmd = ["ss", "-ant"]
    else:
        cmd = ["lsof", "-nPw", "-iTCP"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=flags)
    out, err = p.communicate()
    if err:
        raise RuntimeError(err.decode(errors="ignore"))
    return out.find(b":%d " % port) > 0


def get_available_port() -> int:
    """Returns a port number that is available."""
    with socket.socket() as sock:
        sock.bind(("", 0))
        port = sock.getsockname()[1]
    return port


def wait_for_server(host: str, port: int, timeout: float) -> None:
    """Wait for the 32-bit server to start.

    :param host: The hostname or IP address of the server.
    :param port: The port number of the server.
    :param timeout: The maximum number of seconds to wait to establish a connection to the server.
    :raises ConnectionTimeoutError: If a timeout occurred.
    """
    stop = time.time() + max(0.0, timeout)
    while True:
        if is_port_in_use(port):
            return

        if time.time() > stop:
            raise ConnectionTimeoutError(f"Timeout after {timeout:.1f} second(s). Could not connect to {host}:{port}")


def get_com_info(*additional_keys: str) -> dict[str, dict[str, str | None]]:
    """Reads the registry for the COM_ libraries that are available.

    This function is only supported on Windows.

    .. versionadded:: 0.5

    .. _COM: https://en.wikipedia.org/wiki/Component_Object_Model
    .. _Class ID: https://docs.microsoft.com/en-us/windows/desktop/com/clsid-key-hklm

    :param additional_keys: The Program ID (ProgID) key is returned automatically.
        You can include additional keys (e.g., Version, InprocHandler32, ToolboxBitmap32,
        VersionIndependentProgID, ...) if you also want this additional
        information to be returned for each `Class ID`_.
    :return: The keys are the Class ID's and each value is a :class:`dict`
        of the information that was requested.

    Example::

        >>> from msl.loadlib import utils
        >>> info = utils.get_com_info()
        >>> more_info = utils.get_com_info('Version', 'ToolboxBitmap32')
    """
    if winreg is None:
        return {}

    results = {}
    for item in ["CLSID", r"Wow6432Node\CLSID"]:
        try:
            key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, item)
        except OSError:
            continue
        else:
            logger.debug(r"Parsing HKEY_CLASSES_ROOT\%s\...", item)

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
                progid = winreg.QueryValue(sub_key, "ProgID")
            except OSError:
                pass
            else:
                results[clsid] = {}
                results[clsid]["ProgID"] = progid

                for name in additional_keys:
                    try:
                        results[clsid][name] = winreg.QueryValue(sub_key, name)
                    except OSError:
                        results[clsid][name] = None
            finally:
                winreg.CloseKey(sub_key)

        winreg.CloseKey(key)

    return results


def generate_com_wrapper(lib: Any, out_dir: str | None = None) -> ModuleType:
    """Generate a Python wrapper module around a COM library.

    For more information see `Accessing type libraries`_.

    .. versionadded:: 0.9

    .. _Accessing type libraries: https://pythonhosted.org/comtypes/#accessing-type-libraries

    :param lib: The COM library to create a wrapper of.

        Can be any of the following

            * a :class:`~msl.loadlib.load_library.LoadLibrary` object
            * the `ProgID` or `CLSID` of a registered COM library as a :class:`str`
            * a COM pointer instance (:func:`~ctypes.POINTER`)
            * an ITypeLib COM pointer instance (:func:`~ctypes.POINTER`)
            * a path to a library file (.tlb, .exe or .dll) as a :class:`str`
            * a :class:`tuple` or :class:`list` specifying the GUID of a library,
              a major and a minor version number, plus optionally an LCID number, e.g.,

                 ``['{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}', 1, 1]``

            * an object with ``_reg_libid_`` and ``_reg_version_`` attributes

    :param out_dir: The output directory to save the wrapper to. If not specified,
        the module is saved to the ``../site-packages/comtypes/gen`` directory.
    :return: The wrapper module that was generated.
    """
    if not is_comtypes_installed():
        raise OSError("Cannot create a COM wrapper because comtypes is not installed, run\n  pip install comtypes")

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
        if "LoadLibrary" in str(e):
            mod = from_pointer(lib.lib)
        elif hasattr(lib, "__com_interface__"):
            mod = from_pointer(lib)
        else:
            raise

    if not mod and isinstance(lib, str):
        obj = comtypes.client.CreateObject(lib)
        mod = from_pointer(obj)

    if out_dir is not None:
        comtypes.client.gen_dir = cached_gen_dir

    return mod
