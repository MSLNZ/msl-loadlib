"""
Tests the CLI argparse which updates sys.path,
os.environ['PATH'] and **kwargs for the 32-bit server.
"""
import os
import sys

from msl.loadlib import (
    Server32,
    Client64,
    IS_WINDOWS,
    IS_MAC,
    IS_PYTHON_64BIT,
)

# When the 32-bit Server imports this module on Windows & Python 3.8
# the following exception is raised due to pytest being imported
#    ImportError: No module named 'importlib_metadata'
# The 32-bit server does not require pytest to be imported
if IS_PYTHON_64BIT:
    import pytest
else:
    class Mark(object):
        @staticmethod
        def skipif(condition, reason=None):
            def func(function):
                return function
            return func

    class pytest(object):
        mark = Mark


class ArgParse32(Server32):

    def __init__(self, host, port, **kwargs):
        # load any dll since it won't be called
        path = os.path.join(os.path.dirname(__file__), os.pardir, 'msl', 'examples', 'loadlib', 'cpp_lib32')
        super(ArgParse32, self).__init__(path, 'cdll', host, port)
        self.kwargs = kwargs

    def is_in_sys_path(self, path):
        return os.path.abspath(path) in sys.path

    def is_in_environ_path(self, path):
        return os.path.abspath(path) in os.environ['PATH']

    def get_kwarg(self, key):
        return self.kwargs[key]


class ArgParse64(Client64):

    def __init__(self, append_sys_path, append_environ_path, **kwargs):
        super(ArgParse64, self).__init__(
            __file__,
            append_sys_path=append_sys_path,
            append_environ_path=append_environ_path,
            **kwargs
        )

    def is_in_sys_path(self, path):
        return self.request32('is_in_sys_path', path)

    def is_in_environ_path(self, path):
        return self.request32('is_in_environ_path', path)

    def get_kwarg(self, key):
        return self.request32('get_kwarg', key)


@pytest.mark.skipif(IS_MAC, reason='the 32-bit server for Mac OS does not exist')
def test_argparser():
    if IS_WINDOWS:
        append_sys_path = ['C:/home/joe/code', 'C:/Program Files (x86)/Whatever']
        append_environ_path = ['D:/ends/in/slash/', 'D:/path/to/lib', 'D:/path/with space']
    else:
        append_sys_path = ['/ends/in/slash/', '/usr/local/custom/path']
        append_environ_path = ['/home/my/folder', '/a/path/for/environ/slash/']

    kwargs = {'a': -11, 'b': 3.1415926, 'c': 'abcd efghi jk', 'd': [1, 2, 3], 'e': {1: 'val'}}

    client = ArgParse64(append_sys_path, append_environ_path, **kwargs)

    for path in append_sys_path:
        assert client.is_in_sys_path(path)
    assert client.is_in_sys_path(os.path.dirname(__file__))

    for path in append_environ_path:
        assert client.is_in_environ_path(path)
    assert client.is_in_environ_path(os.getcwd())

    assert client.get_kwarg('a') == '-11'
    assert client.get_kwarg('b') == '3.1415926'
    assert client.get_kwarg('c') == 'abcd efghi jk'
    assert client.get_kwarg('d') == '[1, 2, 3]'
    assert client.get_kwarg('e') == "{1: 'val'}"
