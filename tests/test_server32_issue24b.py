from msl.loadlib import Client64
from msl.loadlib import ConnectionTimeoutError
from msl.loadlib import Server32


if Server32.is_interpreter():
    print("mock skipif_no_server32")

    def skipif_no_server32(*args):
        pass
else:
    import pytest
    from conftest import skipif_no_server32


class HangsForever(Server32):
    def __init__(self, host, port):
        # Simulate the case where instantiating this class on the 32-bit server hangs
        print("import time")
        import time

        print("now go to sleep")
        time.sleep(999)


@skipif_no_server32
def test_instantiating():
    class Issue24(Client64):
        def __init__(self):
            super().__init__(__file__, timeout=2)

    with pytest.warns(UserWarning, match=r"killed the 32-bit server using brute force") as warn_info:
        with pytest.raises(ConnectionTimeoutError, match=r"mock skipif_no_server32\s+import time\s+now go to sleep"):
            Issue24()

    assert len(warn_info.list) == 3

    assert warn_info.list[0].filename == __file__
    assert warn_info.list[0].lineno == 34  # occurs at Issue24() above
    assert str(warn_info.list[0].message) == "killed the 32-bit server using brute force"

    assert warn_info.list[1].filename == __file__
    assert warn_info.list[1].category is ResourceWarning
    assert str(warn_info.list[1].message).startswith("unclosed file")

    assert warn_info.list[2].filename == __file__
    assert warn_info.list[2].category is ResourceWarning
    assert str(warn_info.list[2].message).startswith("unclosed file")
