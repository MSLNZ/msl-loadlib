from __future__ import annotations

import os
import re
import sys
from typing import Any

from msl.loadlib import Client64, Server32

if Server32.is_interpreter():
    from unittest.mock import Mock

    skipif_no_server32 = Mock()
else:
    from conftest import skipif_no_server32


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
def test_protocol() -> None:
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

    # determine the maximum pickle protocol allowed based on
    # Python versions that are used by the server and the client
    server_version = re.match(r"Python\s(\d+)\.(\d+)", Server32.version())
    assert server_version is not None
    server_major, server_minor = map(int, server_version.groups())
    client_major, client_minor = sys.version_info[:2]
    major = min(server_major, client_major)
    minor = min(server_minor, client_minor)
    if major == 2:
        max_protocol = 2
    elif major == 3 and minor < 4:
        max_protocol = 3
    elif major == 3 and minor < 8:
        max_protocol = 4
    else:
        max_protocol = 5

    for protocol in list(range(max_protocol + 2)):
        if protocol > max_protocol:
            with pytest.raises(ValueError, match=r"pickle protocol"):  # noqa: SIM117
                with Bounce64(protocol) as b:
                    pass
        else:
            with Bounce64(protocol) as b:
                a, k = b.bounce(*args, **kwargs)
                assert a == args
                assert k == kwargs
