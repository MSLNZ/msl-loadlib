from msl.loadlib import Client64
from msl.loadlib import ConnectionTimeoutError
from msl.loadlib import Server32

if Server32.is_interpreter():
    # Simulate the case where importing this module on the 32-bit server hangs
    print('importing time')
    import time
    print('sleeping for 999 seconds')
    time.sleep(999)

import pytest
from conftest import skipif_no_server32


@skipif_no_server32
def test_importing():

    class Issue24(Client64):
        def __init__(self):
            super().__init__(__file__, timeout=2)

    with pytest.warns(UserWarning, match=r'killed the 32-bit server using brute force'):
        with pytest.raises(ConnectionTimeoutError, match=r'importing time\s+sleeping for 999 seconds'):
            Issue24()
