import logging
from ctypes import CDLL

import pytest
from py4j.java_gateway import (  # type: ignore[import-untyped] # pyright: ignore[reportMissingTypeStubs]
    JavaGateway,  # pyright: ignore[reportUnknownVariableType]
    JVMView,  # pyright: ignore[reportUnknownVariableType]
)

from conftest import IS_MAC_ARM64, skipif_no_pythonnet, skipif_no_server32
from msl.examples.loadlib import EXAMPLES_DIR, Cpp64
from msl.loadlib import IS_PYTHON_64BIT, LoadLibrary
from msl.loadlib._constants import default_extension
from msl.loadlib.load_library import DotNet
from msl.loadlib.utils import logger

suffix = "arm64" if IS_MAC_ARM64 else "64" if IS_PYTHON_64BIT else "32"


def test_raises() -> None:
    with pytest.raises(OSError, match=r"^Cannot find"):  # noqa: SIM117
        with LoadLibrary("doesnotexist"):
            pass

    with pytest.raises(ValueError, match=r"^Invalid libtype"):  # noqa: SIM117
        with LoadLibrary(EXAMPLES_DIR / "Trig.class", libtype="invalid"):  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
            pass


def test_cpp() -> None:
    path = str(EXAMPLES_DIR / f"cpp_lib{suffix}{default_extension}")
    with LoadLibrary(path) as library:
        assert library.assembly is None
        assert library.gateway is None
        assert library.path == path
        assert isinstance(library.lib, CDLL)
        assert library.lib.add(1, 2) == 3
    assert library.path == path
    assert library.assembly is None
    assert library.gateway is None
    assert library.lib is None

    # can still call this (even multiple times)
    for _ in range(10):  # type: ignore[unreachable]
        library.cleanup()

    assert "libtype=NoneType" in str(library)
    assert "libtype=NoneType" in repr(library)


@skipif_no_pythonnet
def test_dotnet() -> None:
    path = str(EXAMPLES_DIR / f"dotnet_lib{suffix}.dll")
    with LoadLibrary(path, libtype="net") as library:
        assert isinstance(library.assembly, library.lib.System.Reflection.Assembly)
        assert library.assembly is not None
        assert library.gateway is None
        assert library.path == path
        assert isinstance(library.lib, DotNet)
        assert library.lib.DotNetMSL.BasicMath().add_integers(1, 2) == 3  # type: ignore[attr-defined] # pyright: ignore[reportUnknownMemberType,reportAttributeAccessIssue]
    assert library.path == path
    assert library.assembly is None
    assert library.gateway is None
    assert library.lib is None

    # can still call this (even multiple times)
    for _ in range(10):  # type: ignore[unreachable]
        library.cleanup()

    assert "libtype=NoneType" in str(library)
    assert "libtype=NoneType" in repr(library)


def test_java(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG, logger.name)
    path = str(EXAMPLES_DIR / "Trig.class")
    with LoadLibrary(path) as library:
        assert library.assembly is None
        assert isinstance(library.gateway, JavaGateway)
        assert library.path == path
        assert isinstance(library.lib, JVMView)
        assert library.lib.Trig.cos(0.0) == 1.0
    assert library.path == path
    assert library.assembly is None
    assert library.gateway is None
    assert library.lib is None

    record = caplog.records[0]
    assert record.levelname == "DEBUG"
    assert record.msg == "Loaded %s"

    record = caplog.records[1]
    assert record.levelname == "DEBUG"
    assert record.msg == "shutdown Py4J.GatewayServer"

    # can still call this (even multiple times)
    for _ in range(10):
        library.cleanup()

    assert "libtype=NoneType" in str(library)
    assert "libtype=NoneType" in repr(library)


@skipif_no_server32
def test_client() -> None:
    with Cpp64() as cpp:
        assert cpp.connection is not None
        assert cpp.add(1, -1) == 0
    assert cpp.connection is None

    # can still call this (even multiple times)
    for _ in range(10):  # type: ignore[unreachable]
        out, err = cpp.shutdown_server32()
        assert out.closed
        assert err.closed

    with Cpp64() as cpp:
        out, err = cpp.shutdown_server32()
        assert not out.closed
        assert not err.closed
        assert out.read() == b""
        assert err.read() == b""
    out, err = cpp.shutdown_server32()
    assert out.closed
    assert err.closed

    assert str(cpp).endswith("address=None (closed)>")
    assert repr(cpp).endswith("address=None (closed)>")
