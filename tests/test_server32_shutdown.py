import os
import time

from msl.loadlib import Client64
from msl.loadlib import Server32

if Server32.is_interpreter():
    def skipif_no_server32(*args):
        pass
else:
    import pytest
    from conftest import skipif_no_server32


class ShutdownHangs(Server32):

    def __init__(self, host, port):
        path = os.path.join(Server32.examples_dir(), 'cpp_lib32')
        super(ShutdownHangs, self).__init__(path, 'cdll', host, port)

    def add(self, x, y):
        return self.lib.add(x, y)

    def shutdown_handler(self):
        time.sleep(999)


@skipif_no_server32
def test_killed():

    class Hangs(Client64):

        def __init__(self):
            super(Hangs, self).__init__(__file__)

        def add(self, x, y):
            return self.request32('add', x, y)

    hangs = Hangs()
    assert hangs.add(1, 1) == 2
    with pytest.warns(UserWarning, match=r'killed the 32-bit server using brute force'):
        hangs.shutdown_server32(kill_timeout=2)
