import os

from msl.loadlib import Client64, Server32

if Server32.is_interpreter():
    from unittest.mock import Mock

    skipif_no_server32 = Mock()
else:
    from conftest import skipif_no_server32  # type: ignore[assignment]


class Running32(Server32):
    def __init__(self, host: str, port: int) -> None:
        path = os.path.join(Server32.examples_dir(), "cpp_lib32")  # noqa: PTH118
        super().__init__(path, "cdll", host, port)

    def interpreter(self) -> bool:
        return self.is_interpreter()


class Running64(Client64):
    def __init__(self) -> None:
        super().__init__(__file__)

    def interpreter(self) -> bool:
        reply: bool = self.request32("interpreter")
        return reply

    def is_interpreter(self) -> bool:
        reply: bool = self.request32("is_interpreter")
        return reply


@skipif_no_server32
def test_is_interpreter() -> None:  # type: ignore[misc]
    with Running64() as r:
        interpreter = r.interpreter()
        assert isinstance(interpreter, bool)
        assert interpreter

        is_interpreter = r.is_interpreter()
        assert isinstance(is_interpreter, bool)
        assert is_interpreter

        assert not Server32.is_interpreter()
