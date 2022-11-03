from msl.loadlib import Client64
from msl.loadlib import ConnectionTimeoutError
from msl.loadlib import Server32


if Server32.is_interpreter():
    print('mock skipif_no_server32')

    def skipif_no_server32(*args):
        pass
else:
    import pytest
    from conftest import skipif_no_server32


class HangsForever(Server32):
    def __init__(self, host, port):
        # Simulate the case where instantiating this class on the 32-bit server hangs
        print('import time')
        import time
        print('now go to sleep')
        time.sleep(999)


@skipif_no_server32
def test_instantiating():

    class Issue24(Client64):
        def __init__(self):
            super(Issue24, self).__init__(__file__, timeout=2)

    with pytest.warns(UserWarning, match=r'killed the 32-bit server using brute force'):
        with pytest.raises(ConnectionTimeoutError, match=r'mock skipif_no_server32\s+import time\s+now go to sleep'):
            Issue24()
