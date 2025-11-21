"""Common utility functions."""

from __future__ import annotations

import logging
import os
import socket
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING
from xml.etree import ElementTree as ET

try:
    import winreg
except ImportError:
    winreg = None  # type: ignore[assignment]

from ._constants import IS_LINUX, IS_WINDOWS
from .exceptions import ConnectionTimeoutError

if TYPE_CHECKING:
    from types import ModuleType
    from typing import Any

    from .types import PathLike

logger = logging.getLogger(__package__)

_NET_FRAMEWORK_DESCRIPTION: str = """
<!--
  Created by the MSL-LoadLib package.

  By default, applications that target the .NET Framework version 4.0+ cannot load
  assemblies from older .NET Framework versions. You must create and modify the
  <app>.config file and set the useLegacyV2RuntimeActivationPolicy property to be
  "true" for the application to load an assembly from .NET < 4.0.

  For Python.NET to load an assembly from .NET < 4.0, this corresponds to creating
  a python.exe.config (Windows) or python.config (Linux) configuration file that
  is saved in the same directory as the executable.

  See https://support.microsoft.com/kb/2572158 for more information about the
  "Mixed mode assembly" error.
-->
"""

_NET_FRAMEWORK_FIX: str = """
    <startup useLegacyV2RuntimeActivationPolicy="true">
        <supportedRuntime version="v4.0" />
        <supportedRuntime version="v2.0.50727" />
    </startup>
"""


def is_pythonnet_installed() -> bool:
    """Checks if `pythonnet` is installed.

    Returns:
        Whether `pythonnet` is installed.
    """
    try:
        import clr  # type: ignore[import-untyped] # pyright: ignore[reportMissingTypeStubs, reportUnusedImport]  # noqa: F401, PLC0415
    except (ImportError, RuntimeError):
        return False
    return True


def is_py4j_installed() -> bool:
    """Checks if `py4j` is installed.

    Returns:
        Whether `py4j` is installed.

    !!! note "Added in version 0.4"
    """
    try:
        import py4j  # type: ignore[import-untyped] # pyright: ignore[reportMissingTypeStubs, reportUnusedImport]  # noqa: F401, PLC0415
    except ImportError:
        return False
    return True


def is_comtypes_installed() -> bool:
    """Checks if `comtypes` is installed.

    Returns:
        Whether `comtypes` is installed.

    !!! note "Added in version 0.5"
    """
    try:
        import comtypes  # type: ignore[import-untyped] # pyright: ignore[reportMissingTypeStubs, reportUnusedImport]  # noqa: F401, PLC0415
    except ImportError:
        return False
    return True


def check_dot_net_config(py_exe_path: PathLike) -> tuple[int, str]:
    """Checks if the **useLegacyV2RuntimeActivationPolicy** property is enabled.

    By default, [Python.NET](https://pythonnet.github.io/){:target="_blank"} works
    with .NET 4.0+ and therefore it cannot automatically load a library that was compiled
    with .NET &lt; 4.0.

    This function ensures that the **useLegacyV2RuntimeActivationPolicy** property is
    defined in the *py_exe_path*.config file and that it is enabled.

    This [link](https://stackoverflow.com/questions/14508627/){:target="_blank"} provides
    an overview explaining why the **useLegacyV2RuntimeActivationPolicy** property is required.

    The *py_exe_path*.config file that is created is

    ```xml
    <?xml version="1.0" encoding="utf-8" ?>
    <configuration>
        <startup useLegacyV2RuntimeActivationPolicy="true">
            <supportedRuntime version="v4.0" />
            <supportedRuntime version="v2.0.50727" />
        </startup>
    </configuration>
    ```

    Args:
        py_exe_path: The path to a Python executable.

    Returns:
        A status flag and a message describing the outcome.

            The flag will be one of the following values:

            * -1: if there was a problem
            * 0: if the .NET property was already enabled, or
            * 1: if the property was created successfully.
    """
    config_path: str = os.fsdecode(py_exe_path) + ".config"

    if Path(config_path).is_file():
        try:
            tree = ET.parse(config_path)  # noqa: S314
        except ET.ParseError:
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
                f"<configuration>{_NET_FRAMEWORK_FIX}</configuration>\n"
            )
            logger.warning(msg)
            return -1, msg

        # check if the policy exists
        policy = root.find("startup/[@useLegacyV2RuntimeActivationPolicy]")
        if policy is None:
            lines = Path(config_path).read_text().splitlines()
            lines.insert(-1, _NET_FRAMEWORK_FIX)
            _ = Path(config_path).write_text("\n".join(lines))
            msg = (
                f"Added the useLegacyV2RuntimeActivationPolicy property to\n"
                f"{config_path}\n"
                f"Try again to see if Python can now load the .NET library.\n"
            )
            return 1, msg

        if policy.attrib["useLegacyV2RuntimeActivationPolicy"].lower() != "true":
            msg = (
                f'The useLegacyV2RuntimeActivationPolicy attribute is "false" in\n'
                f"{config_path}\n"
                f"Cannot load an assembly from a .NET Framework version < 4.0.\n"
            )
            logger.warning(msg)
            return -1, msg

        return 0, "The useLegacyV2RuntimeActivationPolicy property is enabled"

    text = (
        f'<?xml version="1.0" encoding="utf-8" ?>'
        f"{_NET_FRAMEWORK_DESCRIPTION}"
        f"<configuration>"
        f"{_NET_FRAMEWORK_FIX}"
        f"</configuration>\n"
    )
    _ = Path(config_path).write_text(text)

    msg = (
        f"The library appears to be from a .NET Framework version < 4.0.\n"
        f'To fix the "Mixed mode assembly is built against ..." error\n'
        f"the useLegacyV2RuntimeActivationPolicy property was added to\n"
        f"{config_path}\n\n"
        f"Rerun the script, or restart the interactive console, to see if\n"
        f"Python can now load the .NET library.\n"
    )
    return 1, msg


def is_port_in_use(port: int) -> bool:
    """Checks whether the TCP port is in use.

    Args:
        port: The port number to test.

    Returns:
        Whether the TCP port is in use.

    !!! note "Changed in version 0.10"
        Only check TCP ports (instead of both TCP and UDP ports).
        Uses the ``ss`` command instead of ``netstat`` on Linux.

    !!! note "Changed in version 0.7"
        Renamed from `port_in_use` and added support for macOS.
    """
    flags = 0
    if IS_WINDOWS:
        flags = 0x08000000  # fixes issue 31, CREATE_NO_WINDOW = 0x08000000
        cmd = ["netstat", "-a", "-n", "-p", "TCP"]
    elif IS_LINUX:
        cmd = ["ss", "-ant"]
    else:
        cmd = ["lsof", "-nPw", "-iTCP"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=flags)  # noqa: S603
    out, err = p.communicate()
    if err:
        raise RuntimeError(err.decode(errors="ignore"))
    return out.find(b":%d " % port) > 0


def get_available_port() -> int:
    """[int][] &mdash; Returns a port number that is available."""
    port: int
    with socket.socket() as sock:
        sock.bind(("", 0))
        _, port = sock.getsockname()
        return port


def wait_for_server(host: str, port: int, timeout: float) -> None:
    """Wait for the 32-bit server to start.

    Args:
        host: The hostname or IP address of the server.
        port: The port number of the server.
        timeout: The maximum number of seconds to wait to establish a connection to the server.

    Raises:
        ConnectionTimeoutError: If a timeout occurred.
    """
    stop = time.time() + max(0.0, timeout)
    while True:
        if is_port_in_use(port):
            return

        if time.time() > stop:
            msg = f"Timeout after {timeout:.1f} second(s). Could not connect to {host}:{port}"
            raise ConnectionTimeoutError(msg)


def get_com_info(*additional_keys: str) -> dict[str, dict[str, str | None]]:  # noqa: C901
    """Reads the registry for the [COM]{:target="_blank"} libraries that are available.

    [COM]: https://learn.microsoft.com/en-us/windows/win32/com/component-object-model--com--portal

    !!! attention
        This function is only supported on Windows.

    Args:
        additional_keys: The Program ID (`ProgID`) key is returned automatically.
            You can include additional keys (e.g., `Version`, `InprocHandler32`, `ToolboxBitmap32`,
            `VersionIndependentProgID`, ...) if you also want this additional
            information to be returned for each [Class ID]{:target="_blank"}.

            [Class ID]: https://docs.microsoft.com/en-us/windows/desktop/com/clsid-key-hklm

    **Example:**

    ```python
    from msl.loadlib import utils

    info = utils.get_com_info()
    more_info = utils.get_com_info("Version", "ToolboxBitmap32")
    ```

    Returns:
        The keys are the Class ID's and each value is a [dict][] of the information that was requested.

    !!! note "Added in version 0.5"
    """
    if winreg is None:
        return {}  # type: ignore[unreachable]

    results: dict[str, dict[str, str | None]] = {}
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
                    except OSError:  # noqa: PERF203
                        results[clsid][name] = None
            finally:
                winreg.CloseKey(sub_key)

        winreg.CloseKey(key)

    return results


def generate_com_wrapper(lib: Any, out_dir: PathLike | None = None) -> ModuleType:
    """Generate a Python wrapper module around a [COM]{:target="_blank"} library.

    For more information see [Accessing type libraries]{:target="_blank"}.

    [COM]: https://learn.microsoft.com/en-us/windows/win32/com/component-object-model--com--portal
    [Accessing type libraries]: https://comtypes.readthedocs.io/en/stable/client.html#accessing-type-libraries

    !!! attention
        This function is only supported on Windows.

    Args:
        lib: The COM library to create a wrapper of.

            Can be any of the following:

            * a [LoadLibrary][] instance
            * the `ProgID` or `CLSID` of a registered COM library as a [str][]
            * a `comtypes` pointer instance
            * an `ITypeLib` COM pointer from a loaded type library
            * the path to a library file (.tlb, .exe or .dll) as a [str][]
            * a sequence specifying the `GUID` of a library, a major and a minor
                version number, plus optionally an `LCID` number, e.g.,

                `["{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}", 1, 1]`

            * an object with `_reg_libid_` and `_reg_version_` attributes

        out_dir: The output directory to save the wrapper to. If not specified,
            the module is saved to the `../site-packages/comtypes/gen` directory.

    Returns:
        The wrapper module that was generated.

    !!! note "Added in version 0.9"
    """
    if not is_comtypes_installed():
        msg = "Cannot create a COM wrapper because comtypes is not installed, run\n  pip install comtypes"
        raise OSError(msg)

    import comtypes.client  # type: ignore[import-untyped] # pyright: ignore[reportMissingTypeStubs]  # noqa: PLC0415

    # cache the value of gen_dir to reset it later
    assert isinstance(comtypes.client.gen_dir, str)  # pyright: ignore[reportUnknownMemberType] # noqa: S101
    cached_gen_dir: str = comtypes.client.gen_dir
    if out_dir is not None:
        gen_dir = Path(os.fsdecode(out_dir)).resolve()
        gen_dir.mkdir(parents=True, exist_ok=True)
        comtypes.client.gen_dir = str(gen_dir)

    def from_pointer(p: Any) -> ModuleType:
        info = p.GetTypeInfo(0)
        type_lib, _ = info.GetContainingTypeLib()
        module: ModuleType = comtypes.client.GetModule(type_lib)  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType]
        return module  # pyright: ignore[reportUnknownVariableType]

    mod: ModuleType
    try:
        mod = comtypes.client.GetModule(lib)  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType]
    except OSError:
        if not isinstance(lib, str):
            raise
        obj = comtypes.client.CreateObject(lib)  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType]
        mod = from_pointer(obj)
    except (AttributeError, TypeError) as e:
        if "LoadLibrary" in str(e):
            mod = from_pointer(lib.lib)
        elif hasattr(lib, "__com_interface__"):
            mod = from_pointer(lib)
        else:
            raise

    if out_dir is not None:
        comtypes.client.gen_dir = cached_gen_dir

    return mod  # pyright: ignore[reportUnknownVariableType]
