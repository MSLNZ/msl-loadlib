import os
import sys
from ctypes import c_int
from http.client import HTTPConnection
from unittest.mock import Mock

from conftest import IS_MACOS_ARM64

from msl.loadlib import Client64
from msl.loadlib import Server32
from msl.loadlib import Server32Error

if Server32.is_interpreter():
    pytest = Mock()
    skipif_no_server32 = Mock()
else:
    import pytest
    from conftest import skipif_no_server32
    from msl.loadlib.constants import DEFAULT_EXTENSION


class Server(Server32):

    def __init__(self, host, port, **kwargs):
        if IS_MACOS_ARM64:
            file = 'cpp_libarm64'
        else:
            file = 'cpp_lib64' if sys.maxsize > 2 ** 32 else 'cpp_lib32'
        path = os.path.join(Server32.examples_dir(), file)
        super().__init__(path, 'cdll', host, port)

        self.kwargs = kwargs

        self.lib.add.argtypes = [c_int, c_int]
        self.lib.add.restype = c_int

    def add(self, a, b):
        return self.lib.add(a, b)

    def get_kwargs(self):
        return self.kwargs


class Client(Client64):

    def __init__(self, module32=__file__, host=None, **kwargs):
        super().__init__(module32, host=host, **kwargs)

    def add(self, a, b):
        return self.request32('add', a, b)

    def get_kwargs(self):
        return self.request32('get_kwargs')

    def kwargs(self):
        return self.request32('kwargs')


@skipif_no_server32
@pytest.mark.parametrize('host', [None, '127.0.0.1'])
def test_equivalent(host):
    c = Client(host=host, x=1.2)
    basename = os.path.basename(c.lib32_path)
    if host is None:
        assert c.connection is None
        assert c.host is None
        if sys.maxsize > 2 ** 32:
            # client and server are running in 64-bit Python
            assert c.lib32_path.endswith(f'cpp_lib64{DEFAULT_EXTENSION}')
        else:
            # client and server are running in 32-bit Python
            assert c.lib32_path.endswith(f'cpp_lib32{DEFAULT_EXTENSION}')
        assert c.port == -1
        assert str(c) == f"<Client lib={basename} address=None (mocked)>"
    else:
        assert isinstance(c.connection, HTTPConnection)
        assert c.host == host
        assert c.lib32_path.endswith(f'cpp_lib32{DEFAULT_EXTENSION}')
        assert isinstance(c.port, int) and c.port > 0
        assert str(c) == f"<Client lib={basename} address={host}:{c.port}>"

    assert c.add(1, 2) == 3
    assert c.get_kwargs() == {'x': '1.2'}  # kwarg values are cast to str
    assert c.kwargs() == {'x': '1.2'}  # access attribute value

    # calling shutdown_server32 multiple times is okay
    for _ in range(10):
        stdout, stderr = c.shutdown_server32()
        assert len(stdout.read()) == 0
        assert len(stderr.read()) == 0


def test_attributes():
    c = Client(x=0, y='hello', z=None)
    assert c.connection is None
    assert c.host is None
    if sys.maxsize > 2 ** 32:
        # client and server are running in 64-bit Python
        if IS_MACOS_ARM64:
            assert c.lib32_path.endswith(f'cpp_libarm64{DEFAULT_EXTENSION}')
        else:
            assert c.lib32_path.endswith(f'cpp_lib64{DEFAULT_EXTENSION}')
    else:
        # client and server are running in 32-bit Python
        assert c.lib32_path.endswith(f'cpp_lib32{DEFAULT_EXTENSION}')
    assert c.port == -1
    assert str(c) == f"<Client lib={os.path.basename(c.lib32_path)} address=None (mocked)>"
    assert c.add(1, 2) == 3
    # kwarg values are cast to str
    assert c.get_kwargs() == {'x': '0', 'y': 'hello', 'z': 'None'}
    # access attribute value
    assert c.kwargs() == {'x': '0', 'y': 'hello', 'z': 'None'}

    # calling shutdown_server32 multiple times is okay
    for _ in range(10):
        stdout, stderr = c.shutdown_server32()
        assert len(stdout.read()) == 0
        assert len(stderr.read()) == 0
        stdout.close()
        stderr.close()


def test_context_manager():
    with Client(host=None) as c:
        assert c.add(1, 2) == 3
        assert not c.kwargs()


def test_raises_server32_error():
    c = Client(host=None)
    with pytest.raises(Server32Error, match=r'\(see above for more details\)$'):
        assert c.add(1, [2]) == 3

    stdout, stderr = c.shutdown_server32()
    assert len(stdout.read()) == 0
    assert len(stderr.read()) == 0
    stdout.close()
    stderr.close()


def test_no_server32_subclass():
    mod = os.path.join(os.path.dirname(__file__), 'bad_servers', 'no_server32_subclass.py')
    match = r"no_server32_subclass.py' does not contain a class that is a subclass of Server32$"
    with pytest.raises(AttributeError, match=match):
        Client(module32=mod)


def test_module_not_found():
    with pytest.raises(ModuleNotFoundError):
        Client(module32='does_not_exist')
