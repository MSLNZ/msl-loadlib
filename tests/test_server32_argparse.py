"""
Tests the CLI argparse which updates sys.path,
os.environ['PATH'] and **kwargs for the 32-bit server.
"""
import os
import pathlib
import sys
from unittest.mock import Mock

from msl.loadlib import Client64
from msl.loadlib import Server32
from msl.loadlib import ConnectionTimeoutError

if Server32.is_interpreter():
    pytest = Mock()
    skipif_no_server32 = Mock()
    skipif_not_windows = Mock()
    IS_WINDOWS = Mock()
else:
    import pytest
    from conftest import skipif_no_server32
    from conftest import skipif_not_windows
    from msl.loadlib.constants import IS_WINDOWS


class ArgParse32(Server32):

    def __init__(self, host, port, **kwargs):
        # load any dll since it won't be called
        path = os.path.join(Server32.examples_dir(), 'cpp_lib32')
        super().__init__(path, 'cdll', host, port)
        self.kwargs = kwargs

        self.env_paths = os.environ['PATH'].split(os.pathsep)

        # the server creates the os.added_dll_directories attribute (Windows only)
        try:
            dll_dirs = os.added_dll_directories
        except AttributeError:
            self.dll_dirs = 'os.added_dll_directories does not exist'
        else:
            self.dll_dirs = [p.path for p in dll_dirs]


    @staticmethod
    def is_in_sys_path(path):
        return path in sys.path

    def is_in_environ_path(self, path):
        return path in self.env_paths

    def is_in_dll_dirs(self, path):
        return path in self.dll_dirs

    def get_kwarg(self, key):
        return self.kwargs[key]


class ArgParse64(Client64):

    def __init__(self, **kwargs):
        super().__init__(__file__, **kwargs)

    def is_in_sys_path(self, path):
        p = os.path.abspath(os.fsdecode(path))
        return self.request32('is_in_sys_path', p)

    def is_in_environ_path(self, path):
        p = os.path.abspath(os.fsdecode(path))
        return self.request32('is_in_environ_path', p)

    def is_in_dll_dirs(self, path):
        p = os.path.abspath(os.fsdecode(path))
        return self.request32('is_in_dll_dirs', p)

    def get_kwarg(self, key):
        return self.request32('get_kwarg', key)


class BytesPath:

    def __init__(self, path: bytes) -> None:
        self._path = path

    def __fspath__(self) -> bytes:
        return self._path


@skipif_no_server32
def test_arg_parser_iterable():
    if IS_WINDOWS:
        sys_path = [
            b'C:/home/joe/code',
            'C:\\Program Files (x86)\\Whatever',
            pathlib.Path(r'C:\Users\username'),
            BytesPath(b'C:/users')
        ]
        env_path = [
            b'D:/ends/in/slash/',
            'D:/path/to/lib',
            pathlib.Path(r'D:\path\with space'),
            BytesPath(b'C:/a/b/c')
        ]
        dll_dir = os.path.dirname(__file__)
    else:
        sys_path = [
            b'/ends/in/slash/',
            '/usr/local/custom/path',
            pathlib.Path('/home/username'),
            BytesPath(b'/a/b/c')
        ]
        env_path = [
            b'/home/my/folder',
            '/a/path/for/environ/slash/',
            pathlib.Path('/home/my/username'),
            BytesPath(b'/a/b/c/d')
        ]
        dll_dir = None

    kwargs = {'a': -11, 'b': 3.1415926, 'c': 'abcd efghi jk', 'd': [1, 2, 3], 'e': {1: 'val'}}

    client = ArgParse64(
        add_dll_directory=dll_dir,
        append_sys_path=sys_path,
        append_environ_path=env_path,
        **kwargs)

    for path in sys_path:
        assert client.is_in_sys_path(path)
    assert client.is_in_sys_path(os.path.dirname(__file__))

    for path in env_path:
        assert client.is_in_environ_path(path)
    assert client.is_in_environ_path(os.getcwd())

    if dll_dir is not None:
        assert client.is_in_dll_dirs(dll_dir)

    assert client.get_kwarg('a') == '-11'
    assert client.get_kwarg('b') == '3.1415926'
    assert client.get_kwarg('c') == 'abcd efghi jk'
    assert client.get_kwarg('d') == '[1, 2, 3]'
    assert client.get_kwarg('e') == "{1: 'val'}"


@skipif_not_windows
def test_add_dll_directory_win32():
    with ArgParse64() as a:
        assert a.request32('dll_dirs') == 'os.added_dll_directories does not exist'

    path = os.path.dirname(__file__)
    with ArgParse64(add_dll_directory=path) as a:
        assert a.is_in_dll_dirs(path)

    dll_dirs = [
        path.encode(),
        os.path.abspath(os.path.join(path, '..')),
        pathlib.Path(os.path.abspath(os.path.join(path, '..', '..'))),
        BytesPath(os.path.join(path, 'bad_servers').encode())
    ]
    with ArgParse64(add_dll_directory=dll_dirs) as a:
        for path in dll_dirs:
            assert a.is_in_dll_dirs(path)

    with pytest.raises(ConnectionTimeoutError, match=r'FileNotFoundError'):
        with ArgParse64(add_dll_directory='C:\\does\\not\\exist', timeout=2):
            pass


@pytest.mark.skipif(IS_WINDOWS, reason='do not test on Windows')
@skipif_no_server32
def test_add_dll_directory_linux():
    with pytest.raises(ConnectionTimeoutError, match=r'not supported'):
        with ArgParse64(add_dll_directory='/home', timeout=2):
            pass
