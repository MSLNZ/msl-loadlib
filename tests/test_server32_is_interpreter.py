import os

try:
    import pytest
except ImportError:  # the 32-bit server does not need pytest installed
    class Mark(object):
        @staticmethod
        def skipif(condition, reason=None):
            def func(function):
                return function
            return func

    class pytest(object):
        mark = Mark

from msl.loadlib import Server32, Client64, IS_MAC
from msl.examples.loadlib import EXAMPLES_DIR


class Running32(Server32):

    def __init__(self, host, port, **kwargs):
        super(Running32, self).__init__(
            os.path.join(kwargs['ex_dir'], 'cpp_lib32'),
            'cdll', host, port
        )

    def interpreter(self):
        return self.is_interpreter()


class Running64(Client64):

    def __init__(self):
        super(Running64, self).__init__(__file__, ex_dir=EXAMPLES_DIR)

    def interpreter(self):
        return self.request32('interpreter')

    def is_interpreter(self):
        return self.request32('is_interpreter')


@pytest.mark.skipif(IS_MAC, reason='the 32-bit server for macOS does not exist')
def test_is_interpreter():
    r = Running64()

    interpreter = r.interpreter()
    assert isinstance(interpreter, bool)
    assert interpreter

    is_interpreter = r.is_interpreter()
    assert isinstance(is_interpreter, bool)
    assert is_interpreter

    assert not Server32.is_interpreter()  # this test module is not running on the 32-bit server
