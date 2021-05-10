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


class Ex32(Server32):

    def __init__(self, host, port, **kwargs):
        # this class would not instantiate if Server32.examples_dir()
        # was incorrect, so the fact that the server starts already
        # demonstrates that this test passes
        path = os.path.join(Server32.examples_dir(), 'cpp_lib32')
        super(Ex32, self).__init__(path, 'cdll', host, port)

    def ex_dir(self):
        return self.examples_dir()


class Ex64(Client64):

    def __init__(self):
        super(Ex64, self).__init__(__file__)

    def examples_dir(self):
        return self.request32('examples_dir')

    def ex_dir(self):
        return self.request32('ex_dir')


@pytest.mark.skipif(IS_MAC, reason='the 32-bit server for macOS does not exist')
def test_examples_dir():
    assert Server32.examples_dir() == EXAMPLES_DIR

    e = Ex64()
    assert e.examples_dir() == EXAMPLES_DIR
    assert e.ex_dir() == EXAMPLES_DIR
