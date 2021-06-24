import os
import time

from msl.loadlib import (
    Client64,
    Server32,
    ResponseTimeoutError,
)

if Server32.is_interpreter():
    def skipif_no_server32(*args):
        pass
else:
    import pytest
    from conftest import skipif_no_server32


RPC_TIMEOUT = 5.0


class RPCServer(Server32):

    def __init__(self, host, port):
        path = os.path.join(Server32.examples_dir(), 'cpp_lib32')
        super(RPCServer, self).__init__(path, 'cdll', host, port)

    def no_delay(self, a, b):
        return self.lib.add(a, b)

    def short_delay(self, a, b):
        time.sleep(RPC_TIMEOUT / 2.0)
        return self.lib.add(a, b)

    def long_delay(self, a, b):
        time.sleep(RPC_TIMEOUT * 2.0)
        return self.lib.add(a, b)


class RPCClient(Client64):

    def __init__(self):
        super(RPCClient, self).__init__(__file__, rpc_timeout=RPC_TIMEOUT)

    def no_delay(self, a, b):
        return self.request32('no_delay', a, b)

    def short_delay(self, a, b):
        return self.request32('short_delay', a, b)

    def long_delay(self, a, b):
        return self.request32('long_delay', a, b)


@skipif_no_server32
def test_rpc_timeout():
    c = RPCClient()
    assert c.no_delay(8, 3) == 11
    assert c.short_delay(-4, 2) == -2
    with pytest.raises(ResponseTimeoutError):
        c.long_delay(1, 2)
