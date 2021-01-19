# Make sure that non-callable attributes can be requested from the 32-bit server.
import os
from ctypes import c_float

try:
    import pytest  # the 32-bit server does not need to have access to it
except ImportError:
    pass

from msl.loadlib import Server32, Client64, Server32Error
from msl.examples.loadlib import EXAMPLES_DIR


class Property32(Server32):

    CONSTANT = 2

    def __init__(self, host, port, **kwargs):
        super(Property32, self).__init__(
            os.path.join(kwargs['ex_dir'], 'cpp_lib32'),
            'cdll', host, port
        )

        self.three = self.lib.add(1, 2)

    def subtract(self, a, b):
        self.lib.subtract.restype = c_float
        return self.lib.subtract(c_float(a), c_float(b))

    @property
    def seven(self):
        return 7

    @property
    def parameters(self):
        return {'one': 1, 'string': 'hey', 'complex': 7j}

    @property
    def multiple(self):
        return 1, 'hey', 7j


class Property64(Client64):

    def __init__(self):
        super(Property64, self).__init__(__file__, ex_dir=EXAMPLES_DIR)

        self.CONSTANT = self.request32('CONSTANT')
        self.three = self.request32('three')

    def add(self, a, b):
        return self.request32('add', a, b)

    def subtract(self, a, b):
        return self.request32('subtract', a, b)

    @property
    def seven(self):
        return self.request32('seven')

    @property
    def parameters(self):
        return self.request32('parameters')

    @property
    def foo(self):
        return self.request32('foo')

    def multiple(self):
        return self.request32('multiple')


def test_request_property():
    p = Property64()
    assert p.subtract(100, 100) == 0
    assert p.CONSTANT == 2
    assert p.three == 3
    assert p.seven == 7
    assert p.parameters == {'one': 1, 'string': 'hey', 'complex': 7j}
    assert p.multiple() == (1, 'hey', 7j)

    with pytest.raises(Server32Error, match=r"'Property32' object has no attribute 'add'"):
        p.add(1, 2)

    with pytest.raises(Server32Error, match=r"'Property32' object has no attribute 'foo'"):
        ret = p.foo
