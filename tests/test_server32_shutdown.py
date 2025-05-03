import os
import time

from msl.loadlib import Client64, Server32

if Server32.is_interpreter():
    from unittest.mock import Mock

    skipif_no_server32 = Mock()
else:
    from conftest import skipif_no_server32  # type: ignore[assignment]


class ShutdownHangs(Server32):
    def __init__(self, host: str, port: int) -> None:
        path = os.path.join(Server32.examples_dir(), "cpp_lib32")  # noqa: PTH118
        super().__init__(path, "cdll", host, port)

    def add(self, x: int, y: int) -> int:
        result: int = self.lib.add(x, y)
        return result

    def shutdown_handler(self) -> None:
        time.sleep(999)


@skipif_no_server32
def test_killed() -> None:  # type: ignore[misc]
    import pytest

    class Hangs(Client64):
        def __init__(self) -> None:
            super().__init__(__file__)

        def add(self, x: int, y: int) -> int:
            reply: int = self.request32("add", x, y)
            return reply

    with Hangs() as hangs:
        assert hangs.add(1, 1) == 2
        with pytest.warns(UserWarning, match=r"killed the 32-bit server using brute force") as warn_info:
            _ = hangs.shutdown_server32(kill_timeout=2)

        assert len(warn_info.list) == 1
        assert warn_info.list[0].filename == __file__
        assert warn_info.list[0].lineno == 42  # occurs at hangs.shutdown_server32 above
