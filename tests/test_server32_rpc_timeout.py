import os
import time

from msl.loadlib import Client64, Server32, ResponseTimeoutError, IS_MAC, IS_PYTHON_64BIT

# When the 32-bit Server imports this module on Windows & Python 3.8
# the following exception is raised due to pytest being imported
#    ImportError: No module named 'importlib_metadata'
# The 32-bit server does not require pytest to be imported
if IS_PYTHON_64BIT:
    import pytest
else:
    class Mark(object):
        @staticmethod
        def skipif(condition, reason=None):
            def func(function):
                return function
            return func

    class pytest(object):
        mark = Mark


RPC_TIMEOUT = 5.0


class RPCServer(Server32):

    def __init__(self, host, port, **kwargs):
        path = os.path.join(os.path.dirname(__file__), '..', 'msl', 'examples', 'loadlib', 'cpp_lib32')
        super(RPCServer, self).__init__(os.path.abspath(path), 'cdll', host, port, **kwargs)

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
        super(RPCClient, self).__init__(module32=__file__, rpc_timeout=RPC_TIMEOUT)

    def no_delay(self, a, b):
        return self.request32('no_delay', a, b)

    def short_delay(self, a, b):
        return self.request32('short_delay', a, b)

    def long_delay(self, a, b):
        return self.request32('long_delay', a, b)


@pytest.mark.skipif(IS_MAC, reason='the 32-bit server for macOS does not exist')
def test_rpc_timeout():
    import pytest
    c = RPCClient()
    assert c.no_delay(8, 3) == 11
    assert c.short_delay(-4, 2) == -2
    with pytest.raises(ResponseTimeoutError):
        c.long_delay(1, 2)
