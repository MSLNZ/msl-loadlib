"""Load a library."""

from __future__ import annotations

import ctypes
import ctypes.util
import os
import subprocess
import sys
from typing import TYPE_CHECKING

from . import utils
from .constants import DEFAULT_EXTENSION
from .constants import IS_WINDOWS

if TYPE_CHECKING:
    from typing import Any, TypeVar

    from ._types import LibType, PathLike
    from .activex import Application

    # the Self type was added in Python 3.11 (PEP 673)
    # using TypeVar is equivalent for < 3.11
    if sys.version_info[:2] < (3, 11):
        Self = TypeVar("Self", bound="LoadLibrary")
    else:
        from typing import Self


_LIBTYPES: set[str] = {"cdll", "windll", "oledll", "net", "clr", "java", "com", "activex"}


if IS_WINDOWS and not hasattr(sys, "coinit_flags"):
    # https://pywinauto.readthedocs.io/en/latest/HowTo.html#com-threading-model
    # Configure comtypes for Multi-Threaded Apartment model (MTA)
    # This avoids the following exception from being raised:
    #   [WinError -2147417850] Cannot change thread mode after it is set
    sys.coinit_flags = 0


class LoadLibrary:
    """Load a library."""

    def __init__(self, path: PathLike, libtype: LibType | None = None, **kwargs: Any) -> None:
        """Load a library.

        For example, a C/C++, FORTRAN, .NET, Java, Delphi, LabVIEW, ActiveX, ... library.

        Args:
            path: The path to the library.
                The search order to find the library is:

                1. assume that a full or a relative (to the current working directory) path is specified
                2. use [ctypes.util.find_library][]{:target="_blank"}
                3. search [sys.path][]{:target="_blank"}
                4. search [os.environ["PATH"]][os.environ]{:target="_blank"}.

                If loading a [COM](https://learn.microsoft.com/en-us/windows/win32/com/component-object-model--com--portal){:target="_blank"} library,
                `path` may either be the

                * ProgID (e.g, `"InternetExplorer.Application"`), or the
                * CLSID (e.g., `"{2F7860A2-1473-4D75-827D-6C4E27600CAC}"`).

            libtype: The library type.
                The following values are supported:

                * `cdll`: a library that uses the `__cdecl` calling convention
                    (default value if not specified and not a Java library)
                * `windll` or `oledll`: a library that uses the `__stdcall` calling convention
                * `net` or `clr`: a .NET library (Common Language Runtime)
                * `java`: a Java archive (`.jar` or `.class` files)
                * `com`: a [COM]{:target="_blank"} library
                * `activex`: an [ActiveX]{:target="_blank"} library

                [COM]: https://learn.microsoft.com/en-us/windows/win32/com/component-object-model--com--portal
                [ActiveX]: https://learn.microsoft.com/en-us/windows/win32/com/activex-controls

                !!! tip
                    Since the `.jar` or `.class` extension uniquely defines a Java library,
                    `libtype` will automatically be set to `java` if `path` ends with
                    `.jar` or `.class`.

                !!! note "Support for library types were added in the following `msl-loadlib` versions"
                    * 0.1: __cdecl, __stdcall, .NET
                    * 0.4: Java
                    * 0.5: COM
                    * 0.9: ActiveX

            kwargs: All additional keyword arguments are passed to the object that loads the library.
                If `libtype` is

                * `cdll` &#8594; [ctypes.CDLL][]{:target="_blank"}
                * `windll` &#8594; [ctypes.WinDLL][]{:target="_blank"}
                * `oledll` &#8594; [ctypes.OleDLL][]{:target="_blank"}
                * `net` or `clr` &#8594; all keyword arguments are ignored
                * `java` &#8594; [JavaGateway][py4j.java_gateway.JavaGateway]{:target="_blank"}
                * `com` &#8594; [comtypes.CreateObject][CreateObject]{:target="_blank"}
                * `activex` &#8594; [Application.load][msl.loadlib.activex.Application.load]

        Raises:
            OSError: If the library cannot be loaded.
            ValueError: If the value of `libtype` is not supported.
        """
        # a reference to the ActiveX application
        self._app = None

        # a reference to the library
        self._lib = None

        # a reference to the .NET Runtime Assembly
        self._assembly = None

        # a reference to the Py4J JavaGateway
        self._gateway = None

        if not path:
            msg = f"Must specify a non-empty path, got {path!r}"
            raise ValueError(msg)

        # fixes Issue #8, if `path` is a <class 'pathlib.Path'> object
        path = os.fsdecode(path)

        if libtype is None:
            # automatically determine the libtype
            if path.endswith(".jar") or path.endswith(".class"):
                libtype = "java"
            else:
                libtype = "cdll"
        else:
            libtype = libtype.lower()

        if libtype not in _LIBTYPES:
            msg = f"Invalid libtype {libtype!r}\nMust be one of: {', '.join(_LIBTYPES)}"
            raise ValueError(msg)

        # create a new reference to `path` just in case the
        # DEFAULT_EXTENSION is appended below so that the
        # ctypes.util.find_library function call will use the
        # unmodified value of `path`
        _path = path

        # assume a default extension if no extension was provided
        ext = os.path.splitext(path)[1]
        if not ext and libtype not in ["java", "com", "activex"]:
            _path += DEFAULT_EXTENSION

        if libtype not in ["com", "activex"]:
            self._path = os.path.abspath(_path)
            if not os.path.isfile(self._path):
                # for find_library use the original 'path' value since it may be a library name
                # without any prefix like 'lib', suffix like '.so', '.dylib' or version number
                self._path = ctypes.util.find_library(path)
                if self._path is None:  # then search sys.path and os.environ['PATH']
                    success = False
                    search_dirs = sys.path + os.environ["PATH"].split(os.pathsep)
                    for directory in search_dirs:
                        p = os.path.join(directory, _path)
                        if os.path.isfile(p):
                            self._path = p
                            success = True
                            break
                    if not success:
                        msg = f"Cannot find {path!r} for libtype={libtype!r}"
                        raise OSError(msg)
        else:
            self._path = _path

        if libtype == "cdll":
            self._lib = ctypes.CDLL(self._path, **kwargs)
        elif libtype == "windll":
            self._lib = ctypes.WinDLL(self._path, **kwargs)
        elif libtype == "oledll":
            self._lib = ctypes.OleDLL(self._path, **kwargs)
        elif libtype == "com":
            if not utils.is_comtypes_installed():
                msg = "Cannot load a COM library because comtypes is not installed.\nRun: pip install comtypes"
                raise OSError(msg)

            from comtypes import GUID
            from comtypes.client import CreateObject

            try:
                clsid = GUID.from_progid(self._path)
            except (TypeError, OSError):
                clsid = None

            if clsid is None:
                msg = f"Cannot find {path!r} for libtype='com'"
                raise OSError(msg)

            self._lib = CreateObject(clsid, **kwargs)

        elif libtype == "activex":
            from .activex import Application

            self._app = Application()
            self._lib = self._app.load(self._path, **kwargs)

        elif libtype == "java":
            if not utils.is_py4j_installed():
                msg = "Cannot load a Java file because Py4J is not installed.\nRun: pip install py4j"
                raise OSError(msg)

            from py4j.version import __version__
            from py4j.java_gateway import JavaGateway, GatewayParameters

            # the address and port to use to host the py4j.GatewayServer
            address = kwargs.pop("address", "127.0.0.1")
            port = kwargs.pop("port", utils.get_available_port())

            # find the py4j*.jar file (needed to import the py4j.GatewayServer on the Java side)
            filename = f"py4j{__version__}.jar"
            py4j_jar = os.environ.get("PY4J_JAR", "")
            if py4j_jar:
                if not os.path.isfile(py4j_jar) or os.path.basename(py4j_jar) != filename:
                    msg = (
                        f"A PY4J_JAR environment variable exists, "
                        f"but the full path to {filename} is invalid\n"
                        f"PY4J_JAR={py4j_jar}"
                    )
                    raise OSError(msg)
            else:
                root = os.path.dirname(sys.executable)
                for item in [root, os.path.dirname(root), os.path.join(os.path.expanduser("~"), ".local")]:
                    py4j_jar = os.path.join(item, "share", "py4j", filename)
                    if os.path.isfile(py4j_jar):
                        break
                if not os.path.isfile(py4j_jar):
                    msg = (
                        f"Cannot find {filename}\n"
                        f"Create a PY4J_JAR environment variable "
                        f"to be equal to the full path to {filename}"
                    )
                    raise OSError(msg)

            # build the java command
            wrapper = os.path.join(os.path.dirname(__file__), "py4j-wrapper.jar")
            cmd = ["java", "-cp", f"{py4j_jar}{os.pathsep}{wrapper}", "Py4JWrapper", str(port)]

            # from the URLClassLoader documentation:
            #   Any URL that ends with a '/' is assumed to refer to a directory. Otherwise, the URL
            #   is assumed to refer to a JAR file which will be downloaded and opened as needed.
            if ext == ".jar":
                cmd.append(self._path)
            else:  # it is a .class file
                cmd.append(f"{os.path.dirname(self._path)}/")

            err = None
            try:
                # start the py4j.GatewayServer
                flags = 0x08000000 if IS_WINDOWS else 0  # fixes issue 31, CREATE_NO_WINDOW = 0x08000000
                subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, creationflags=flags)
            except OSError as e:
                err = str(e).rstrip()
                err += "\nYou must have a Java Runtime Environment installed and available on PATH"

            if err:
                raise OSError(err)

            try:
                utils.wait_for_server(address, port, 10.0)
            except OSError as e:
                err = str(e).rstrip()
                err += "\nCould not start the Py4J GatewayServer"

            if err:
                raise OSError(err)

            self._gateway = JavaGateway(gateway_parameters=GatewayParameters(address=address, port=port, **kwargs))

            self._lib = self._gateway.jvm

        elif libtype == "net" or libtype == "clr":
            if not utils.is_pythonnet_installed():
                msg = "Cannot load a .NET Assembly because pythonnet is not installed.\nRun: pip install pythonnet"
                raise OSError(msg)

            import clr  # noqa: clr is an alias for pythonnet
            import System  # noqa: available once pythonnet is imported

            dotnet = {"System": System}

            # the library must be available in sys.path
            head, tail = os.path.split(self._path)
            sys.path.insert(0, head)

            try:
                # don't include the library extension
                clr.AddReference(os.path.splitext(tail)[0])  # noqa: AddReference exists
            except (System.IO.FileNotFoundException, System.IO.FileLoadException):
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
                if str(err).startswith("Mixed mode assembly is built against version"):
                    py_exe = sys.executable
                    if sys.prefix != sys.base_prefix:
                        # Python is running in a venv/virtualenv
                        # When using conda environments, sys.prefix == sys.base_prefix
                        py_exe = os.path.join(sys.base_prefix, os.path.basename(py_exe))
                    status, msg = utils.check_dot_net_config(py_exe)
                    if status == 0:
                        msg = f"Checking .NET config returned {msg!r} and still cannot load the library.\n{err}"
                    raise OSError(msg)

                msg = "The above 'System.IO.FileLoadException' is not handled.\n"
                raise OSError(msg)

            try:
                types = self._assembly.GetTypes()
            except Exception as e:
                utils.logger.error(e)
                utils.logger.error("The LoaderExceptions are:")
                for item in e.LoaderExceptions:  # noqa: LoaderExceptions comes from .NET
                    utils.logger.error("  %s", item.Message)
            else:
                for t in types:
                    try:
                        if t.Namespace:
                            obj = __import__(t.Namespace)
                        else:
                            obj = getattr(__import__("clr"), t.FullName)
                    except:  # noqa: PEP 8: E722 do not use bare 'except'
                        obj = t
                        obj.__name__ = t.FullName

                    if obj.__name__ not in dotnet:
                        dotnet[obj.__name__] = obj

            self._lib = DotNet(self._path, dotnet)

        else:
            assert False, "Should not get here -- contact developers"

        utils.logger.debug("Loaded %s", self._path)

    def __del__(self) -> None:
        """Calls cleanup."""
        if hasattr(self, "_gateway"):
            self.cleanup()

    def __repr__(self) -> str:
        """Returns the string representation."""
        lib_name: str = self._lib.__class__.__name__
        return f"<{self.__class__.__name__} libtype={lib_name} path={self._path}>"

    def __enter__(self: Self) -> Self:
        """Enter a context manager."""
        return self

    def __exit__(self, *ignore) -> None:
        """Exit a context manager."""
        self.cleanup()

    @property
    def application(self) -> Application | None:
        """[Application][msl.loadlib.activex.Application] | `None` &mdash; Reference to the ActiveX application window.

        If the loaded library is not an ActiveX library, returns `None`.

        When an ActiveX library is loaded, the window is not shown
        (to show it call [Application.show][msl.loadlib.activex.Application.show])
        and the message loop is not running
        (to run it call [Application.run][msl.loadlib.activex.Application.run]).

        !!! note "Added in version 1.0"
        """
        return self._app

    def cleanup(self) -> None:
        """Clean up references to the library.

        !!! note "Added in version 0.10"
        """
        self._assembly = None
        self._lib = None
        if self._gateway:
            self._gateway.shutdown()
            self._gateway = None
            utils.logger.debug("shutdown Py4J.GatewayServer")
        if self._app:
            self._app.close()
            self._app = None
            utils.logger.debug("close ActiveX application")

    @property
    def assembly(self) -> Any:
        """Returns a reference to the [.NET Runtime Assembly]{:target="_blank"} object.

        If the loaded library is not a .NET library, returns `None`.

        !!! tip
            The [JetBrains dotPeek]{:target="_blank"} program can be used to decompile a .NET Assembly.

        [.NET Runtime Assembly]: https://docs.microsoft.com/en-us/dotnet/api/system.reflection.assembly
        [JetBrains dotPeek]: https://www.jetbrains.com/decompiler/
        """
        return self._assembly

    @property
    def gateway(self):
        """[JavaGateway][py4j.java_gateway.JavaGateway] | `None` &mdash; Reference to the Java gateway.

        If the loaded library is not a Java library, returns `None`.
        """
        return self._gateway

    @property
    def lib(self) -> Any:
        """Returns the reference to the library object.

        For example, if `libtype` is

        * `cdll` &#8594; [ctypes.CDLL][]{:target="_blank"}
        * `windll` &#8594; [ctypes.WinDLL][]{:target="_blank"}
        * `oledll` &#8594; [ctypes.OleDLL][]{:target="_blank"}
        * `java` &#8594; [JVMView][py4j.java_gateway.JVMView]{:target="_blank"}
        * `net` or `clr` &#8594; An object containing .NET [namespace]{:target="_blank"}s,
            classes and [System.Type]{:target="_blank"}s
        * `com` or `activex` &#8594; [ctypes.POINTER][]{:target="_blank"}

        [namespace]: https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/namespace
        [System.Type]: https://learn.microsoft.com/en-us/dotnet/api/system.type
        """
        return self._lib

    @property
    def path(self) -> str:
        """[str][] &mdash; The path to the library file."""
        return self._path


class DotNet:
    """Container class for .NET objects."""

    def __init__(self, path: str, items: dict[str, Any]) -> None:
        """Contains the namespaces, classes and System.Type objects of a .NET Assembly.

        Args:
            path: The path to the .NET library file.
            items: The items to use to update the internal __dict__ attribute.
        """
        self._path: str = path
        self.__dict__.update(items)

    def __repr__(self) -> str:
        """Returns the string representation."""
        return f"<{self.__class__.__name__} path={self._path}>"
