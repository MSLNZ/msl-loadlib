"""Tests the CLI argparse which updates sys.path, os.environ['PATH'] and **kwargs for the 32-bit server."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from msl.loadlib import Client64, ConnectionTimeoutError, Server32

if Server32.is_interpreter():
    from unittest.mock import Mock

    pytest = Mock()
    skipif_no_server32 = Mock()
    skipif_not_windows = Mock()
else:
    import pytest  # type: ignore[assignment]

    from conftest import skipif_no_server32, skipif_not_windows  # type: ignore[assignment]

IS_WINDOWS: bool = sys.platform == "win32"


class BytesPath:
    def __init__(self, path: bytes) -> None:
        self._path: bytes = path

    def __fspath__(self) -> bytes:
        return self._path


class ArgParse32(Server32):
    def __init__(self, host: str, port: int, **kwargs: str) -> None:
        # load any dll since it won't be called
        path = os.path.join(Server32.examples_dir(), "cpp_lib32")  # noqa: PTH118
        super().__init__(path, "cdll", host, port)
        self.kwargs: dict[str, str] = kwargs

        self.env_paths: list[str] = os.environ["PATH"].split(os.pathsep)

        # the server creates the os.added_dll_directories attribute (Windows only)
        self.dll_dirs: str | list[str]
        try:
            dll_dirs = os.added_dll_directories  # type: ignore[attr-defined] # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType,reportUnknownVariableType]
        except AttributeError:
            self.dll_dirs = "os.added_dll_directories does not exist"
        else:
            self.dll_dirs = [p.path for p in dll_dirs]  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType]

    @staticmethod
    def is_in_sys_path(path: str) -> bool:
        return path in sys.path

    def is_in_environ_path(self, path: str) -> bool:
        return path in self.env_paths

    def is_in_dll_dirs(self, path: str) -> bool:
        return path in self.dll_dirs

    def get_kwarg(self, key: str) -> str:
        value: str = self.kwargs[key]
        return value


class ArgParse64(Client64):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(__file__, **kwargs)

    def is_in_sys_path(self, path: str | bytes | Path | BytesPath) -> bool:
        p = os.path.abspath(os.fsdecode(path))  # noqa: PTH100
        reply: bool = self.request32("is_in_sys_path", p)
        return reply

    def is_in_environ_path(self, path: str | bytes | Path | BytesPath) -> bool:
        p = os.path.abspath(os.fsdecode(path))  # noqa: PTH100
        reply: bool = self.request32("is_in_environ_path", p)
        return reply

    def is_in_dll_dirs(self, path: str | bytes | Path | BytesPath) -> bool:
        p = os.path.abspath(os.fsdecode(path))  # noqa: PTH100
        reply: bool = self.request32("is_in_dll_dirs", p)
        return reply

    def get_kwarg(self, key: str) -> str:
        reply: str = self.request32("get_kwarg", key)
        return reply


@skipif_no_server32
def test_arg_parser_iterable() -> None:  # type: ignore[misc]
    sys_path: list[bytes | str | Path | BytesPath]
    env_path: list[bytes | str | Path | BytesPath]
    if IS_WINDOWS:
        sys_path = [
            b"C:/home/joe/code",
            "C:\\Program Files (x86)\\Whatever",
            Path(r"C:\Users\username"),
            BytesPath(b"C:/users"),
        ]
        env_path = [
            b"D:/ends/in/slash/",
            "D:/path/to/lib",
            Path(r"D:\path\with space"),
            BytesPath(b"C:/a/b/c"),
        ]
        dll_dir = os.path.dirname(__file__)  # noqa: PTH120
    else:
        sys_path = [
            b"/ends/in/slash/",
            "/usr/local/custom/path",
            Path("/home/username"),
            BytesPath(b"/a/b/c"),
        ]
        env_path = [
            b"/home/my/folder",
            "/a/path/for/environ/slash/",
            Path("/home/my/username"),
            BytesPath(b"/a/b/c/d"),
        ]
        dll_dir = None

    kwargs = {"a": -11, "b": 3.1415926, "c": "abcd efghi jk", "d": [1, 2, 3], "e": {1: "val"}}  # cSpell: ignore efghi

    client = ArgParse64(add_dll_directory=dll_dir, append_sys_path=sys_path, append_environ_path=env_path, **kwargs)

    for path in sys_path:
        assert client.is_in_sys_path(path)
    assert client.is_in_sys_path(Path(__file__).parent)

    for path in env_path:
        assert client.is_in_environ_path(path)
    assert client.is_in_environ_path(Path.cwd())

    if dll_dir is not None:
        assert client.is_in_dll_dirs(dll_dir)

    assert client.get_kwarg("a") == "-11"
    assert client.get_kwarg("b") == "3.1415926"
    assert client.get_kwarg("c") == "abcd efghi jk"
    assert client.get_kwarg("d") == "[1, 2, 3]"
    assert client.get_kwarg("e") == "{1: 'val'}"


@skipif_not_windows
def test_add_dll_directory_win32() -> None:  # type: ignore[misc]
    with ArgParse64() as a:
        assert a.request32("dll_dirs") == "os.added_dll_directories does not exist"

    path = str(Path(__file__).parent)
    with ArgParse64(add_dll_directory=path) as a:
        assert a.is_in_dll_dirs(path)

    dll_dirs: list[bytes | str | Path | BytesPath] = [
        path.encode(),
        os.path.abspath(os.path.join(path, "..")),  # noqa: PTH100, PTH118
        Path(os.path.abspath(os.path.join(path, "..", ".."))),  # noqa: PTH100, PTH118
        BytesPath(os.path.join(path, "bad_servers").encode()),  # noqa: PTH118
    ]
    with ArgParse64(add_dll_directory=dll_dirs) as a:
        for item in dll_dirs:
            assert a.is_in_dll_dirs(item)

    with pytest.raises(ConnectionTimeoutError, match=r"FileNotFoundError"):  # noqa: SIM117
        with ArgParse64(add_dll_directory="C:\\does\\not\\exist", timeout=5):
            pass


@pytest.mark.skipif(IS_WINDOWS, reason="do not test on Windows")  # type: ignore[misc]
@skipif_no_server32
def test_add_dll_directory_linux() -> None:  # type: ignore[misc]
    with pytest.raises(ConnectionTimeoutError, match=r"not supported"):  # noqa: SIM117
        with ArgParse64(add_dll_directory="/home", timeout=2):
            pass
