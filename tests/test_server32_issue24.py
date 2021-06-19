import time

from msl.loadlib import (
    Server32,
    Client64,
    IS_MAC,
    IS_PYTHON_64BIT,
    ConnectionTimeoutError,
)

# When the 32-bit Server imports this module on Windows & Python 3.8
# the following exception is raised due to pytest being imported
#    ImportError: No module named 'importlib_metadata'
# The 32-bit server does not require pytest to be imported
if IS_PYTHON_64BIT:
    import pytest
else:
    class Mark(object):
        @staticmethod
        def skipif(condition, reason=None):
            def func(function):
                return function
            return func

    class pytest(object):
        mark = Mark


class HangsForever(Server32):
    def __init__(self, host, port):
        time.sleep(999)


@pytest.mark.skipif(IS_MAC, reason='the 32-bit server for macOS does not exist')
def test_issue24():
    class Issue24(Client64):
        def __init__(self):
            super(Issue24, self).__init__(__file__, timeout=2)

    with pytest.warns(UserWarning, match=r'killed the 32-bit server using brute force'):
        with pytest.raises(ConnectionTimeoutError):
            Issue24()
