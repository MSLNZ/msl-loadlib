import time

from msl.loadlib import (
    Server32,
    Client64,
    ConnectionTimeoutError,
)

if Server32.is_interpreter():
    def skipif_no_server32(*args):
        pass
else:
    import pytest
    from conftest import skipif_no_server32


class HangsForever(Server32):
    def __init__(self, host, port):
        time.sleep(999)


@skipif_no_server32
def test_issue24():

    class Issue24(Client64):
        def __init__(self):
            super(Issue24, self).__init__(__file__, timeout=2)

    with pytest.warns(UserWarning, match=r'killed the 32-bit server using brute force'):
        with pytest.raises(ConnectionTimeoutError):
            Issue24()
