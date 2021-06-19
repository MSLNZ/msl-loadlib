import os
import time

from msl.examples.loadlib import EXAMPLES_DIR
from msl.loadlib import (
    Server32,
    Client64,
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


class ShutdownHangs(Server32):

    def __init__(self, host, port, path=None):
        p = os.path.join(path, 'cpp_lib32')
        super(ShutdownHangs, self).__init__(p, 'cdll', host, port)

    def add(self, x, y):
        return self.lib.add(x, y)

    def shutdown_handler(self):
        time.sleep(999)


@pytest.mark.skipif(IS_MAC, reason='the 32-bit server for macOS does not exist')
def test_killed():

    class Hangs(Client64):

        def __init__(self):
            super(Hangs, self).__init__(__file__, path=EXAMPLES_DIR)

        def add(self, x, y):
            return self.request32('add', x, y)

    hangs = Hangs()
    assert hangs.add(1, 1) == 2
    with pytest.warns(UserWarning, match=r'killed the 32-bit server using brute force'):
        hangs.shutdown_server32(kill_timeout=2)
