import os

from msl.examples.loadlib import EXAMPLES_DIR
from msl.loadlib import Client64
from msl.loadlib import Server32

if Server32.is_interpreter():

    def skipif_no_server32(*args):
        pass
else:
    from conftest import skipif_no_server32


class Ex32(Server32):
    def __init__(self, host, port, **kwargs):
        # this class would not instantiate if Server32.examples_dir()
        # was incorrect, so the fact that the server starts already
        # demonstrates that this test passes
        path = os.path.join(Server32.examples_dir(), "cpp_lib32")
        super().__init__(path, "cdll", host, port)

    def ex_dir(self):
        return self.examples_dir()


class Ex64(Client64):
    def __init__(self):
        super().__init__(__file__)

    def examples_dir(self):
        return self.request32("examples_dir")

    def ex_dir(self):
        return self.request32("ex_dir")


@skipif_no_server32
def test_examples_dir():
    assert Server32.examples_dir() == EXAMPLES_DIR

    e = Ex64()
    assert e.examples_dir() == str(EXAMPLES_DIR)
    assert e.ex_dir() == str(EXAMPLES_DIR)
