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

    @staticmethod
    def running():
        return Server32.is_running()


class Running64(Client64):

    def __init__(self):
        super(Running64, self).__init__(__file__, ex_dir=EXAMPLES_DIR)

    def running(self):
        return self.request32('running')


@pytest.mark.skipif(IS_MAC, reason='the 32-bit server for macOS does not exist')
def test_remove_site_packages_64bit():
    r = Running64()
    is_running = r.running()
    assert isinstance(is_running, bool)
    assert is_running
    assert not Server32.is_running()  # this test module is not running on the 32-bit server
