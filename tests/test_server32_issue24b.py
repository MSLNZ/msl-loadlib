from msl.loadlib import Client64, ConnectionTimeoutError, Server32

if Server32.is_interpreter():
    from unittest.mock import Mock

    skipif_no_server32 = Mock()
    print("mock skipif_no_server32")  # noqa: T201
else:
    from conftest import skipif_no_server32  # type: ignore[assignment]


class HangsForever(Server32):
    def __init__(self, host: str, port: int) -> None:
        # Simulate the case where instantiating this class on the 32-bit server hangs
        print("import time")  # noqa: T201
        import time  # noqa: PLC0415

        print("now go to sleep")  # noqa: T201
        for _ in range(999):
            time.sleep(1)

        super().__init__("whatever", "cdll", host, port)


@skipif_no_server32
def test_instantiating() -> None:  # type: ignore[misc]
    import pytest  # noqa: PLC0415

    class Issue24(Client64):
        def __init__(self) -> None:
            super().__init__(__file__, timeout=2)

    with pytest.warns(UserWarning, match=r"killed the 32-bit server using brute force") as warn_info:  # noqa: PT031, SIM117
        with pytest.raises(ConnectionTimeoutError, match=r"mock skipif_no_server32\s+import time\s+now go to sleep"):
            with Issue24():  # this line is what the lineno test should equal
                pass

    assert len(warn_info.list) == 3

    assert warn_info.list[0].filename == __file__
    assert warn_info.list[0].lineno == 35  # occurs at "with Issue24():" above
    assert str(warn_info.list[0].message) == "killed the 32-bit server using brute force"

    assert warn_info.list[1].filename == __file__
    assert warn_info.list[1].category is ResourceWarning
    assert str(warn_info.list[1].message).startswith("unclosed file")

    assert warn_info.list[2].filename == __file__
    assert warn_info.list[2].category is ResourceWarning
    assert str(warn_info.list[2].message).startswith("unclosed file")
