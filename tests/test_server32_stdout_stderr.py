from __future__ import print_function
import os
import sys

from msl.loadlib import Server32, Client64
from msl.examples.loadlib import EXAMPLES_DIR


class Print32(Server32):

    def __init__(self, host, port, path=None):
        super(Print32, self).__init__(os.path.join(path, 'cpp_lib32'), 'cdll', host, port)
        print('this is a message')
        print('there is a problem', file=sys.stderr)


class Print64(Client64):

    def __init__(self):
        super(Print64, self).__init__(__file__, path=EXAMPLES_DIR)


def test_shutdown_server32():

    p = Print64()
    stdout, stderr = p.shutdown_server32()
    assert stdout.read().rstrip() == b'this is a message'
    assert stderr.read().rstrip() == b'there is a problem'

    # calling shutdown_server32 multiple times is okay
    # but the buffer has been read already
    for _ in range(10):
        stdout, stderr = p.shutdown_server32()
        assert not stdout.read()
        assert not stderr.read()
