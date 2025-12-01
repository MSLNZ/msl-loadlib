from __future__ import annotations

import os
import platform
import sys
from ctypes import c_int
from http.client import HTTPConnection
from pathlib import Path
from typing import Any

from msl.loadlib import Client64, Server32, Server32Error

if Server32.is_interpreter():
    from unittest.mock import Mock

    pytest = Mock()
    skipif_no_server32 = Mock()
    default_extension = ""
else:
    import pytest  # type: ignore[assignment]

    from conftest import skipif_no_server32  # type: ignore[assignment]
    from msl.loadlib._constants import default_extension


IS_MACOS_ARM64 = sys.platform == "darwin" and platform.machine() == "arm64"


class Server(Server32):
    def __init__(self, host: str, port: int, **kwargs: str) -> None:
        arch = "arm64" if IS_MACOS_ARM64 else "64" if sys.maxsize > 2**32 else "32"
        path = os.path.join(Server32.examples_dir(), f"cpp_lib{arch}")  # noqa: PTH118
        super().__init__(path, "cdll", host, port)

        self.kwargs: dict[str, str] = kwargs

        self.lib.add.argtypes = [c_int, c_int]
        self.lib.add.restype = c_int

    def add(self, a: int, b: int) -> int:
        out: int = self.lib.add(a, b)
        return out

    def get_kwargs(self) -> dict[str, str]:
        return self.kwargs


class Client(Client64):
    def __init__(self, module32: str | Path = __file__, host: str | None = None, **kwargs: Any) -> None:
        super().__init__(module32, host=host, **kwargs)

    def add(self, a: int, b: int) -> int:
        reply: int = self.request32("add", a, b)
        return reply

    def get_kwargs(self) -> dict[str, str]:
        # calls the method
        reply: dict[str, str] = self.request32("get_kwargs")
        return reply

    def kwargs(self) -> dict[str, str]:
        # calls the attribute
        reply: dict[str, str] = self.request32("kwargs")
        return reply


@skipif_no_server32
@pytest.mark.parametrize("host", [None, "127.0.0.1"])  # type: ignore[untyped-decorator]
def test_equivalent(host: None | str) -> None:  # type: ignore[misc]
    c = Client(host=host, x=1.2)
    basename = Path(c.lib32_path).name
    if host is None:
        assert c.connection is None
        assert c.host is None
        if sys.maxsize > 2**32:
            # client and server are running in 64-bit Python
            assert c.lib32_path.endswith(f"cpp_lib64{default_extension}")
        else:
            # client and server are running in 32-bit Python
            assert c.lib32_path.endswith(f"cpp_lib32{default_extension}")
        assert c.port == -1
        assert str(c) == f"<Client lib={basename} address=None (mocked)>"
    else:
        assert isinstance(c.connection, HTTPConnection)
        assert c.host == host
        assert c.lib32_path.endswith(f"cpp_lib32{default_extension}")
        assert isinstance(c.port, int)
        assert c.port > 0
        assert str(c) == f"<Client lib={basename} address={host}:{c.port}>"

    assert c.add(1, 2) == 3
    assert c.get_kwargs() == {"x": "1.2"}  # kwarg values are cast to str
    assert c.kwargs() == {"x": "1.2"}  # access attribute value

    # calling shutdown_server32 multiple times is okay
    for _ in range(10):
        stdout, stderr = c.shutdown_server32()
        assert len(stdout.read()) == 0
        assert len(stderr.read()) == 0


def test_attributes() -> None:
    c = Client(x=0, y="hello", z=None)
    assert c.connection is None
    assert c.host is None
    if sys.maxsize > 2**32:
        # client and server are running in 64-bit Python
        if IS_MACOS_ARM64:
            assert c.lib32_path.endswith(f"cpp_libarm64{default_extension}")
        else:
            assert c.lib32_path.endswith(f"cpp_lib64{default_extension}")
    else:
        # client and server are running in 32-bit Python
        assert c.lib32_path.endswith(f"cpp_lib32{default_extension}")
    assert c.port == -1
    assert str(c) == f"<Client lib={Path(c.lib32_path).name} address=None (mocked)>"
    assert c.add(1, 2) == 3
    # kwarg values are cast to str
    assert c.get_kwargs() == {"x": "0", "y": "hello", "z": "None"}
    # access attribute value
    assert c.kwargs() == {"x": "0", "y": "hello", "z": "None"}

    # calling shutdown_server32 multiple times is okay
    for _ in range(10):
        stdout, stderr = c.shutdown_server32()
        assert len(stdout.read()) == 0
        assert len(stderr.read()) == 0
        stdout.close()
        stderr.close()


def test_context_manager() -> None:
    with Client(host=None) as c:
        assert c.add(1, 2) == 3
        assert not c.kwargs()


def test_raises_server32_error() -> None:
    c = Client(host=None)
    with pytest.raises(Server32Error, match=r"\(see above for more details\)$"):
        assert c.add(1, [2]) == 3  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]

    stdout, stderr = c.shutdown_server32()
    assert len(stdout.read()) == 0
    assert len(stderr.read()) == 0
    stdout.close()
    stderr.close()


def test_no_server32_subclass() -> None:
    mod = Path(__file__).parent / "bad_servers" / "no_server32_subclass.py"
    match = r"no_server32_subclass.py' does not contain a class that is a subclass of Server32$"
    with pytest.raises(AttributeError, match=match):
        _ = Client(module32=mod)


def test_module_not_found() -> None:
    with pytest.raises(ModuleNotFoundError):
        _ = Client(module32="does_not_exist")
