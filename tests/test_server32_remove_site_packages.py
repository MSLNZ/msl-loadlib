import os
import sys

from msl.loadlib import Client64, Server32

if Server32.is_interpreter():
    from unittest.mock import Mock

    skipif_no_server32 = Mock()
else:
    from conftest import skipif_no_server32  # type: ignore[assignment]


class Site32(Server32):
    def __init__(self, host: str, port: int) -> None:
        path = os.path.join(Server32.examples_dir(), "cpp_lib32")  # noqa: PTH118
        super().__init__(path, "cdll", host, port)

    def remove(self) -> str:
        return self.remove_site_packages_64bit()

    @staticmethod
    def contains(path: str) -> bool:
        return path in sys.path


class Site64(Client64):
    def __init__(self) -> None:
        super().__init__(__file__)

    def remove(self) -> str:
        reply: str = self.request32("remove")
        return reply

    def contains(self, path: str) -> bool:
        reply: bool = self.request32("contains", path)
        return reply


@skipif_no_server32
def test_remove() -> None:  # type: ignore[misc]
    with Site64() as s:
        path = s.remove()
        assert path
        assert path in sys.path
        assert not s.contains(path)
