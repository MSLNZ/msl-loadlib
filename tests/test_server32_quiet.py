"""
Make sure that the old syntax where Server32 required a `quiet` argument is still valid.
"""
import os

from msl.loadlib import Server32, Client64
from msl.examples.loadlib import EXAMPLES_DIR


class Quiet32(Server32):

    def __init__(self, host, port, quiet, **kwargs):
        super(Quiet32, self).__init__(
            os.path.join(kwargs['ex_dir'], 'cpp_lib32'),
            'cdll', host, port, quiet
        )
        self._kwargs = kwargs

    def add(self, a, b):
        return self.lib.add(a, b)

    def kwargs(self):
        return self._kwargs


class Quiet64(Client64):

    def __init__(self, **kwargs):
        super(Quiet64, self).__init__(__file__, **kwargs)

    def add(self, a, b):
        # a and b must be integers
        return self.request32('add', a, b)

    def kwargs(self):
        return self.request32('kwargs')


def test_server32_quiet_argument():

    q = Quiet64(one=1, array=[1., -2.2, 3e9], ex_dir=EXAMPLES_DIR)

    assert q.add(-5, 2) == -3
    assert q.kwargs() == {'one': '1', 'array': '[1.0, -2.2, 3000000000.0]', 'ex_dir': EXAMPLES_DIR}
