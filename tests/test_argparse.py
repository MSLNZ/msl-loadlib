from msl.loadlib import IS_WINDOWS
from msl.examples.loadlib.cli64 import ClientArgParse


def test_argparser():

    if IS_WINDOWS:
        append_sys_path = ['C:/home/joe/code', 'C:/Program Files (x86)/Whatever']
        append_environ_path = ['D:/ends/in/slash/', 'D:/path/to/lib', 'D:/path/with space']
    else:
        append_sys_path = ['/ends/in/slash/', '/usr/local/custom/path']
        append_environ_path = ['/home/my/folder', '/a/path/for/environ/slash/']

    kwargs = {'a': -11, 'b': 3.1415926, 'c': 'abcd efghi jk', 'd': [1, 2, 3], 'e': {1: 'val'}}

    client = ClientArgParse(append_sys_path, append_environ_path, **kwargs)

    for path in append_sys_path:
        assert client.is_in_sys_path(path)

    for path in append_environ_path:
        assert client.is_in_environ_path(path)

    assert client.get_kwarg('a') == '-11'
    assert client.get_kwarg('b') == '3.1415926'
    assert client.get_kwarg('c') == 'abcd efghi jk'
    assert client.get_kwarg('d') == '[1, 2, 3]'
    assert client.get_kwarg('e') == "{1: 'val'}"
