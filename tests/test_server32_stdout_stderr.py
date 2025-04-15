from __future__ import print_function

import os
import sys

from msl.loadlib import Client64
from msl.loadlib import Server32

if Server32.is_interpreter():

    def skipif_no_server32(*args):
        pass
else:
    from conftest import skipif_no_server32


class Print32(Server32):
    def __init__(self, host, port, **kwargs):
        path = os.path.join(Server32.examples_dir(), "cpp_lib32")
        super().__init__(path, "cdll", host, port)

        if kwargs["show"] == "True":
            print("this is a message")
            print("there is a problem", file=sys.stderr)

    def write(self, n, stdout):
        stream = sys.stdout if stdout else sys.stderr
        print("x" * n, end="", file=stream)
        return True


class Print64(Client64):
    def __init__(self, show):
        super().__init__(__file__, show=show)

    def write(self, n, stdout):
        return self.request32("write", n, stdout)


@skipif_no_server32
def test_shutdown_server32():
    p = Print64(True)
    stdout, stderr = p.shutdown_server32()
    assert stdout.read().rstrip() == b"this is a message"
    assert stderr.read().rstrip() == b"there is a problem"

    # calling shutdown_server32 multiple times is okay
    # but the buffer has been read already
    for _ in range(10):
        stdout, stderr = p.shutdown_server32()
        assert not stdout.read()
        assert not stderr.read()


@skipif_no_server32
def test_buffer_size_4096():
    # 4096 is the maximum buffer size for a PIPE before the 32-bit server blocks
    n = 4096
    p = Print64(False)
    assert p.write(n, True)
    assert p.write(n, False)
    stdout, stderr = p.shutdown_server32()
    assert stdout.read() == b"x" * n
    assert stderr.read() == b"x" * n

    # calling shutdown_server32 multiple times is okay
    # but the buffer has been read already
    for _ in range(10):
        stdout, stderr = p.shutdown_server32()
        assert not stdout.read()
        assert not stderr.read()
