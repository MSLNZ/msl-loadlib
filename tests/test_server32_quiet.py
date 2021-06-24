import os
import subprocess

from msl.loadlib import Server32, Client64, SERVER_FILENAME
from msl.examples.loadlib import EXAMPLES_DIR

if Server32.is_interpreter():
    def skipif_no_server32(*args):
        pass
else:
    from conftest import skipif_no_server32


class Quiet32(Server32):

    def __init__(self, host, port, quiet, **kwargs):
        path = os.path.join(Server32.examples_dir(), 'cpp_lib32')
        super(Quiet32, self).__init__(path, 'cdll', host, port, quiet)
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


@skipif_no_server32
def test_quiet_argument():
    # Make sure that the old syntax where Server32 required a `quiet` argument is still valid.
    q = Quiet64(one=1, array=[1., -2.2, 3e9], ex_dir=EXAMPLES_DIR)
    assert q.add(-5, 2) == -3
    assert q.kwargs() == {'one': '1', 'array': '[1.0, -2.2, 3000000000.0]', 'ex_dir': EXAMPLES_DIR}


@skipif_no_server32
def test_cli_quiet_flag():
    cmd = [os.path.join(os.path.dirname(__file__), os.pardir, 'msl', 'loadlib', SERVER_FILENAME), '--quiet']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    assert out.rstrip() == b'DeprecationWarning: the --quiet flag is ignored and will be removed in a future release'

    lines = err.splitlines()
    assert lines[0] == b'You must specify a Python module to run on the 32-bit server.'
    assert lines[1] == b'For example: ' + SERVER_FILENAME.encode() + b' -m my_module'
    assert lines[2] == b'Cannot start the 32-bit server.'
