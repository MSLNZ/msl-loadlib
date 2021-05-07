import os
import sys

try:
    import pytest
except ImportError:  # the 32-bit server does not need pytest installed
    class Mark(object):
        @staticmethod
        def skipif(condition, reason=None):
            def func(function):
                return function
            return func

    class pytest(object):
        mark = Mark

from msl.loadlib import Server32, Client64, IS_MAC, IS_PYTHON2
from msl.examples.loadlib import EXAMPLES_DIR


class Site32(Server32):

    def __init__(self, host, port, **kwargs):
        super(Site32, self).__init__(
            os.path.join(kwargs['ex_dir'], 'cpp_lib32'),
            'cdll', host, port
        )

    def remove(self):
        return self.remove_site_packages_64bit()

    @staticmethod
    def contains(path):
        return path in sys.path


class Site64(Client64):

    def __init__(self):
        super(Site64, self).__init__(__file__, ex_dir=EXAMPLES_DIR)

    def remove(self):
        return self.request32('remove')

    def contains(self, path):
        return self.request32('contains', path)


@pytest.mark.skipif(IS_MAC, reason='the 32-bit server for macOS does not exist')
def test_remove_site_packages_64bit():
    s = Site64()
    path = s.remove()
    assert path
    if IS_PYTHON2:
        # get rid of the UnicodeWarning that gets printed by pytest
        assert path.encode() in sys.path
    else:
        assert path in sys.path
    assert not s.contains(path)
