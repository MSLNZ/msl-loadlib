import os
import time

from msl.loadlib import Client64, ResponseTimeoutError, Server32

if Server32.is_interpreter():
    from unittest.mock import Mock

    skipif_no_server32 = Mock()
else:
    from conftest import skipif_no_server32  # type: ignore[assignment]


RPC_TIMEOUT = 5.0


class RPCServer(Server32):
    def __init__(self, host: str, port: int) -> None:
        path = os.path.join(Server32.examples_dir(), "cpp_lib32")  # noqa: PTH118
        super().__init__(path, "cdll", host, port)

    def no_delay(self, a: int, b: int) -> int:
        result: int = self.lib.add(a, b)
        return result

    def short_delay(self, a: int, b: int) -> int:
        time.sleep(RPC_TIMEOUT / 2.0)
        result: int = self.lib.add(a, b)
        return result

    def long_delay(self, a: int, b: int) -> int:
        time.sleep(RPC_TIMEOUT * 2.0)
        result: int = self.lib.add(a, b)
        return result


class RPCClient(Client64):
    def __init__(self) -> None:
        super().__init__(__file__, rpc_timeout=RPC_TIMEOUT)

    def no_delay(self, a: int, b: int) -> int:
        reply: int = self.request32("no_delay", a, b)
        return reply

    def short_delay(self, a: int, b: int) -> int:
        reply: int = self.request32("short_delay", a, b)
        return reply

    def long_delay(self, a: int, b: int) -> int:
        reply: int = self.request32("long_delay", a, b)
        return reply


@skipif_no_server32
def test_rpc_timeout() -> None:  # type: ignore[misc]
    import pytest

    with RPCClient() as c:
        assert c.no_delay(8, 3) == 11
        assert c.short_delay(-4, 2) == -2
        with pytest.raises(ResponseTimeoutError):
            _ = c.long_delay(1, 2)
