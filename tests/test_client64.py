import gc
import os.path
import pathlib
from datetime import datetime

import pytest

from conftest import skipif_no_server32
from conftest import skipif_not_windows
from msl.examples.loadlib import Cpp64
from msl.examples.loadlib import EXAMPLES_DIR
from msl.loadlib import Client64
from msl.loadlib.client64 import _build_paths
from msl.loadlib.constants import SERVER_FILENAME


@skipif_no_server32
def test_unclosed_warnings_1(recwarn):
    # recwarn is a built-in pytest fixture that records all warnings emitted by test functions

    # The following warnings should not be written to stderr for the unclosed subprocess PIPE's
    #   sys:1: ResourceWarning: unclosed file <_io.BufferedReader name=3>
    #   sys:1: ResourceWarning: unclosed file <_io.BufferedReader name=4>
    # nor for unclosed sockets
    #   ResourceWarning: unclosed <socket.socket ...>

    Cpp64()
    gc.collect()
    assert len(recwarn) == 0


@skipif_no_server32
def test_unclosed_warnings_2(recwarn):
    for _ in range(3):
        cpp = Cpp64()
        out, err = cpp.shutdown_server32()
        for _ in range(10):
            out.close()
            err.close()
        del cpp
    gc.collect()
    assert len(recwarn) == 0


def test_bad_del():
    # Make sure that the following exception is not raised in Client64.__del__
    #   AttributeError: 'BadDel' object has no attribute '_conn'

    class BadDel(Client64):
        def __init__(self):
            pass

    b = BadDel()
    b.__del__()
    del b

    with BadDel():
        pass

    # this should raise AttributeError because super() was not called in BadDel
    with pytest.raises(AttributeError, match='_client'):
        BadDel().request32('request')


def test_invalid_server32_dir():
    with pytest.raises(OSError, match=rf'^Cannot find {SERVER_FILENAME}$'):
        Client64(__file__, server32_dir='')


@skipif_no_server32
@skipif_not_windows
def test_module32_as_name():
    client = Client64(module32='msl.examples.loadlib.kernel32')
    assert isinstance(client.request32('get_time'), datetime)


@skipif_no_server32
@skipif_not_windows
def test_module32_as_path():
    path = os.path.join(EXAMPLES_DIR, 'kernel32.py')
    assert os.path.isfile(path)
    client = Client64(module32=path)
    assert isinstance(client.request32('get_time'), datetime)


def test_build_paths_none():
    paths = _build_paths(None)
    assert isinstance(paths, list)
    assert len(paths) == 0


class BytesPath:

    def __init__(self, path: bytes) -> None:
        self._path = path

    def __fspath__(self) -> bytes:
        return self._path


@pytest.mark.parametrize('path', ['here', b'here', pathlib.Path('here'), BytesPath(b'here')])
def test_build_paths_single(path):
    assert _build_paths(path) == [os.path.join(os.getcwd(), 'here')]


def test_build_paths_iterable():
    cwd = os.getcwd()
    paths = ['a', b'b', pathlib.Path('c'), BytesPath(b'd')]
    assert _build_paths(paths) == [
        os.path.join(cwd, 'a'),
        os.path.join(cwd, 'b'),
        os.path.join(cwd, 'c'),
        os.path.join(cwd, 'd'),
    ]


def test_build_paths_ignore():
    cwd = os.getcwd()
    paths = ['a', b'b', pathlib.Path('c'), BytesPath(b'd')]
    assert _build_paths(paths, ignore=[os.path.join(cwd, 'c')]) == [
        os.path.join(cwd, 'a'),
        os.path.join(cwd, 'b'),
        os.path.join(cwd, 'd'),
    ]
