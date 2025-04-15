import os
import sys

from msl.loadlib import Client64
from msl.loadlib import Server32

if Server32.is_interpreter():
    def skipif_no_server32(*args):
        pass
else:
    from conftest import skipif_no_server32


class Site32(Server32):

    def __init__(self, host, port):
        path = os.path.join(Server32.examples_dir(), "cpp_lib32")
        super().__init__(path, "cdll", host, port)

    def remove(self):
        return self.remove_site_packages_64bit()

    @staticmethod
    def contains(path):
        return path in sys.path


class Site64(Client64):

    def __init__(self):
        super().__init__(__file__)

    def remove(self):
        return self.request32("remove")

    def contains(self, path):
        return self.request32("contains", path)


@skipif_no_server32
def test_remove():
    s = Site64()
    path = s.remove()
    assert path
    assert path in sys.path
    assert not s.contains(path)
