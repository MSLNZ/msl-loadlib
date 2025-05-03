from __future__ import annotations

import os
from ctypes import c_float

from msl.loadlib import Client64, Server32, Server32Error

if Server32.is_interpreter():
    from unittest.mock import Mock

    skipif_no_server32 = Mock()
else:
    from conftest import skipif_no_server32  # type: ignore[assignment]


class Property32(Server32):
    CONSTANT: int = 2

    def __init__(self, host: str, port: int) -> None:
        path = os.path.join(Server32.examples_dir(), "cpp_lib32")  # noqa: PTH118
        super().__init__(path, "cdll", host, port)

        self.three: int = self.lib.add(1, 2)

    def subtract(self, a: float, b: float) -> float:
        self.lib.subtract.restype = c_float
        result: float = self.lib.subtract(c_float(a), c_float(b))
        return result

    @property
    def seven(self) -> int:
        return 7

    @property
    def parameters(self) -> dict[str, int | str | complex]:
        return {"one": 1, "string": "hey", "complex": 7j}

    @property
    def multiple(self) -> tuple[int, str, complex]:
        return 1, "hey", 7j


class Property64(Client64):
    def __init__(self) -> None:
        super().__init__(__file__)

        self.CONSTANT: int = self.request32("CONSTANT")
        self.three: int = self.request32("three")

    def add(self, a: int, b: int) -> int:
        reply: int = self.request32("add", a, b)
        return reply

    def subtract(self, a: float, b: float) -> float:
        reply: float = self.request32("subtract", a, b)
        return reply

    @property
    def seven(self) -> int:
        reply: int = self.request32("seven")
        return reply

    @property
    def parameters(self) -> dict[str, int | str | complex]:
        reply: dict[str, int | str | complex] = self.request32("parameters")
        return reply

    @property
    def foo(self) -> int:
        reply: int = self.request32("foo")
        return reply

    def multiple(self) -> tuple[int, str, complex]:
        reply: tuple[int, str, complex] = self.request32("multiple")
        return reply


@skipif_no_server32
def test_request_property() -> None:  # type: ignore[misc]
    import pytest

    with Property64() as p:
        assert p.subtract(100, 100) == 0
        assert p.CONSTANT == 2
        assert p.three == 3
        assert p.seven == 7
        assert p.parameters == {"one": 1, "string": "hey", "complex": 7j}
        assert p.multiple() == (1, "hey", 7j)

        with pytest.raises(Server32Error, match=r"'Property32' object has no attribute 'add'"):
            _ = p.add(1, 2)

        with pytest.raises(Server32Error, match=r"'Property32' object has no attribute 'foo'"):
            _ = p.foo
