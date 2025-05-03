import os
import sys

from msl.loadlib import Client64, Server32

if Server32.is_interpreter():
    from unittest.mock import Mock

    skipif_no_server32 = Mock()
else:
    from conftest import skipif_no_server32  # type: ignore[assignment]


class Print32(Server32):
    def __init__(self, host: str, port: int, **kwargs: str) -> None:
        path = os.path.join(Server32.examples_dir(), "cpp_lib32")  # noqa: PTH118
        super().__init__(path, "cdll", host, port)

        if kwargs["show"] == "True":
            print("this is a message")  # noqa: T201
            print("there is a problem", file=sys.stderr)  # noqa: T201

    def write(self, n: int, *, stdout: bool) -> bool:
        stream = sys.stdout if stdout else sys.stderr
        print("x" * n, end="", file=stream)
        return True


class Print64(Client64):
    def __init__(self, *, show: bool) -> None:
        super().__init__(__file__, show=show)

    def write(self, n: int, *, stdout: bool) -> bool:
        reply: bool = self.request32("write", n, stdout=stdout)
        return reply


@skipif_no_server32
def test_shutdown_server32() -> None:  # type: ignore[misc]
    p = Print64(show=True)
    stdout, stderr = p.shutdown_server32()
    assert stdout.read().rstrip() == b"this is a message"
    assert stderr.read().rstrip() == b"there is a problem"

    # calling shutdown_server32 multiple times is okay
    # but the buffer has been read already
    for _ in range(10):
        stdout, stderr = p.shutdown_server32()
        assert not stdout.read()
        assert not stderr.read()


@skipif_no_server32
def test_buffer_size_4096() -> None:  # type: ignore[misc]
    # 4096 is the maximum buffer size for a PIPE before the 32-bit server blocks
    n = 4096
    p = Print64(show=False)
    assert p.write(n, stdout=True)
    assert p.write(n, stdout=False)
    stdout, stderr = p.shutdown_server32()
    assert stdout.read() == b"x" * n
    assert stderr.read() == b"x" * n

    # calling shutdown_server32 multiple times is okay
    # but the buffer has been read already
    for _ in range(10):
        stdout, stderr = p.shutdown_server32()
        assert not stdout.read()
        assert not stderr.read()
