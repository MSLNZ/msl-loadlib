from __future__ import annotations

import gc
import os.path
from datetime import datetime
from pathlib import Path

import pytest

from conftest import skipif_no_server32, skipif_not_windows
from msl.examples.loadlib import EXAMPLES_DIR, Cpp64
from msl.loadlib import Client64
from msl.loadlib._constants import server_filename
from msl.loadlib.client64 import _build_paths  # pyright: ignore[reportPrivateUsage]


@skipif_no_server32
def test_unclosed_warnings_1(recwarn: pytest.WarningsRecorder) -> None:
    # recwarn is a built-in pytest fixture that records all warnings emitted by test functions

    # The following warnings should not be written to stderr for the unclosed subprocess PIPE's
    #   sys:1: ResourceWarning: unclosed file <_io.BufferedReader name=3>
    #   sys:1: ResourceWarning: unclosed file <_io.BufferedReader name=4>
    # nor for unclosed sockets
    #   ResourceWarning: unclosed <socket.socket ...>
    Cpp64()  # pyright: ignore[reportUnusedCallResult]
    _ = gc.collect()
    assert len(recwarn) == 0


@skipif_no_server32
def test_unclosed_warnings_2(recwarn: pytest.WarningsRecorder) -> None:
    for _ in range(3):
        cpp = Cpp64()
        out, err = cpp.shutdown_server32()
        for _ in range(10):
            out.close()
            err.close()
        del cpp
    _ = gc.collect()
    assert len(recwarn) == 0


def test_bad_del() -> None:
    # Make sure that the following exception is not raised in Client64.__del__
    #   AttributeError: 'BadDel' object has no attribute '_client'

    class BadDel(Client64):
        def __init__(self) -> None:  # pyright: ignore[reportMissingSuperCall]
            pass

    b = BadDel()
    b.__del__()
    del b

    with BadDel():
        pass

    # this should raise AttributeError because super() was not called in BadDel
    with pytest.raises(AttributeError, match="_client"):
        BadDel().request32("request")


def test_invalid_server32_dir() -> None:
    with pytest.raises(OSError, match=rf"^Cannot find {server_filename}$"):
        _ = Client64(__file__, server32_dir="")


@skipif_no_server32
@skipif_not_windows
def test_module32_as_name() -> None:
    # Load the kernel32 module because it uses an absolute path to kernel32.dll
    # Trying to load another module will look for the shared library in the tmp/_MEI*
    # directory since Path(__file__).parent is used to locate the shared library
    with Client64("msl.examples.loadlib.kernel32") as c:
        assert isinstance(c.request32("get_local_time"), datetime)


@skipif_no_server32
@skipif_not_windows
def test_module32_as_path() -> None:
    # Load the kernel32 file because it uses an absolute path to kernel32.dll
    # Trying to load another module will look for the shared library in the tmp/_MEI*
    # directory since Path(__file__).parent is used to locate the shared library
    path = EXAMPLES_DIR / "kernel32.py"
    assert path.is_file()
    client = Client64(path)
    assert isinstance(client.request32("get_local_time"), datetime)


def test_build_paths_none() -> None:
    paths = _build_paths(None)
    assert isinstance(paths, list)
    assert len(paths) == 0


class BytesPath:
    def __init__(self, path: bytes) -> None:
        self._path: bytes = path

    def __fspath__(self) -> bytes:
        return self._path


@pytest.mark.parametrize("path", ["here", b"here", Path("here"), BytesPath(b"here")])
def test_build_paths_single(path: str | bytes | Path | BytesPath) -> None:
    assert _build_paths(path) == [os.path.join(os.getcwd(), "here")]  # noqa: PTH109, PTH118


def test_build_paths_iterable() -> None:
    cwd = os.getcwd()  # noqa: PTH109
    paths: list[str | bytes | Path | BytesPath] = ["a", b"b", Path("c"), BytesPath(b"d")]
    assert _build_paths(paths) == [
        os.path.join(cwd, "a"),  # noqa: PTH118
        os.path.join(cwd, "b"),  # noqa: PTH118
        os.path.join(cwd, "c"),  # noqa: PTH118
        os.path.join(cwd, "d"),  # noqa: PTH118
    ]


def test_build_paths_ignore() -> None:
    cwd = os.getcwd()  # noqa: PTH109
    paths: list[str | bytes | Path | BytesPath] = ["a", b"b", Path("c"), BytesPath(b"d")]
    assert _build_paths(paths, ignore=[os.path.join(cwd, "c")]) == [  # noqa: PTH118
        os.path.join(cwd, "a"),  # noqa: PTH118
        os.path.join(cwd, "b"),  # noqa: PTH118
        os.path.join(cwd, "d"),  # noqa: PTH118
    ]
