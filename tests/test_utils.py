import pytest

from msl.loadlib import utils


def test_timeout():
    with pytest.raises(utils.ConnectionTimeoutError):
        utils.wait_for_server('localhost', utils.get_available_port(), 2)


def test_port_functions():
    assert not utils.port_in_use(utils.get_available_port())
