from __future__ import annotations

import os
from typing import Any

from msl.loadlib import Client64, Server32

if Server32.is_interpreter():
    from unittest.mock import Mock

    skipif_no_server32 = Mock()
else:
    from conftest import skipif_no_server32  # type: ignore[assignment]


class Bounce32(Server32):
    def __init__(self, host: str, port: int) -> None:
        path = os.path.join(Server32.examples_dir(), "cpp_lib32")  # noqa: PTH118
        super().__init__(path, "cdll", host, port)

    def bounce(self, *args: Any, **kwargs: Any) -> Any:
        return args, kwargs


class Bounce64(Client64):
    def __init__(self, protocol: int) -> None:
        super().__init__(__file__, protocol=protocol)

    def bounce(self, *args: Any, **kwargs: Any) -> Any:
        return self.request32("bounce", *args, **kwargs)


@skipif_no_server32
def test_protocol() -> None:  # type: ignore[misc]
    import pytest

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

    for protocol in [0, 1, 2, 3, 4, 5]:
        with Bounce64(protocol) as b:
            a, k = b.bounce(*args, **kwargs)
            assert a == args
            assert k == kwargs

    with pytest.raises(ValueError, match=r"pickle protocol"):  # noqa: SIM117
        with Bounce64(6) as b:
            pass
