import os

from msl.loadlib import Client64
from msl.loadlib import Server32

if Server32.is_interpreter():
    def skipif_no_server32(*args):
        pass
else:
    from conftest import skipif_no_server32


class Running32(Server32):

    def __init__(self, host, port):
        path = os.path.join(Server32.examples_dir(), 'cpp_lib32')
        super(Running32, self).__init__(path, 'cdll', host, port)

    def interpreter(self):
        return self.is_interpreter()


class Running64(Client64):

    def __init__(self):
        super(Running64, self).__init__(__file__)

    def interpreter(self):
        return self.request32('interpreter')

    def is_interpreter(self):
        return self.request32('is_interpreter')


@skipif_no_server32
def test_is_interpreter():
    r = Running64()

    interpreter = r.interpreter()
    assert isinstance(interpreter, bool)
    assert interpreter

    is_interpreter = r.is_interpreter()
    assert isinstance(is_interpreter, bool)
    assert is_interpreter

    assert not Server32.is_interpreter()
