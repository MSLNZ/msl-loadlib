from msl.loadlib import Client64, ConnectionTimeoutError, Server32

if Server32.is_interpreter():
    # Simulate the case where importing this module on the 32-bit server hangs
    print("importing time")  # noqa: T201
    import time

    print("sleeping for 999 seconds")  # noqa: T201
    for _ in range(999):
        time.sleep(1)

import pytest

from conftest import skipif_no_server32


@skipif_no_server32
def test_importing() -> None:
    class Issue24(Client64):
        def __init__(self) -> None:
            super().__init__(__file__, timeout=2)

    with pytest.warns(UserWarning, match=r"killed the 32-bit server using brute force"):  # noqa: SIM117
        with pytest.raises(ConnectionTimeoutError, match=r"importing time\s+sleeping for 999 seconds"):
            with Issue24():
                pass
