from pathlib import Path

from msl.examples.loadlib import EXAMPLES_DIR
from msl.loadlib import Client64, Server32

if Server32.is_interpreter():
    from unittest.mock import Mock

    skipif_no_server32 = Mock()
else:
    from conftest import skipif_no_server32  # type: ignore[assignment]


class Ex32(Server32):
    def __init__(self, host: str, port: int) -> None:
        # this class would not instantiate if Server32.examples_dir()
        # was incorrect, so the fact that the server starts already
        # demonstrates that this test passes
        super().__init__(Server32.examples_dir() / "cpp_lib32", "cdll", host, port)

    def ex_dir(self) -> Path:
        return self.examples_dir()


class Ex64(Client64):
    def __init__(self) -> None:
        super().__init__(__file__)

    def examples_dir(self) -> Path:
        reply: Path = self.request32("examples_dir")
        return reply

    def ex_dir(self) -> Path:
        reply: Path = self.request32("ex_dir")
        return reply


@skipif_no_server32
def test_examples_dir() -> None:  # type: ignore[misc]
    assert Server32.examples_dir() == EXAMPLES_DIR

    with Ex64() as e:
        assert e.examples_dir() == EXAMPLES_DIR
        assert e.ex_dir() == EXAMPLES_DIR
