import os
import re
import sys

from msl.loadlib import Client64
from msl.loadlib import Server32
from msl.loadlib import Server32Error

if Server32.is_interpreter():

    def skipif_no_server32(*args):
        pass
else:
    import pytest
    from conftest import skipif_no_server32


class Bounce32(Server32):
    def __init__(self, host, port):
        path = os.path.join(Server32.examples_dir(), "cpp_lib32")
        super().__init__(path, "cdll", host, port)

    def bounce(self, *args, **kwargs):
        return args, kwargs


class Bounce64(Client64):
    def __init__(self, protocol):
        super().__init__(__file__, protocol=protocol)

    def bounce(self, *args, **kwargs):
        return self.request32("bounce", *args, **kwargs)


@skipif_no_server32
def test_protocol():
    args = (None, True, False, 1, -2.0, 5 - 6j, [1, [2.0, "hello"]], {"one": "1", "two": 2})
    kwargs = {
        "None": None,
        "True": True,
        "False": False,
        "Int": 1,
        "Float": -2.0,
        "Complex": 5 - 6j,
        "List": [1, [2.0, "hello"]],
        "Dict": {"one": "1", "two": 2},
    }

    # determine the maximum pickle protocol allowed based on
    # Python versions that are used by the server and the client
    server_version = re.match(r"Python\s(\d+)\.(\d+)", Server32.version())
    server_major, server_minor = map(int, server_version.groups())
    client_major, client_minor = sys.version_info[:2]
    major = min(server_major, client_major)
    minor = min(server_minor, client_minor)
    if major == 2:
        max_protocol = 2
    elif major == 3 and minor < 4:
        max_protocol = 3
    elif major == 3 and minor < 8:
        max_protocol = 4
    else:
        max_protocol = 5

    for protocol in list(range(10)):
        if protocol > max_protocol:
            with pytest.raises((Server32Error, ValueError), match=r"pickle protocol"):
                Bounce64(protocol)
        else:
            b = Bounce64(protocol)
            a, k = b.bounce(*args, **kwargs)
            assert a == args
            assert k == kwargs
