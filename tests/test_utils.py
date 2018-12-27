import os
import xml.etree.ElementTree as ET

import pytest

from msl.loadlib import utils, IS_WINDOWS


def test_timeout():
    with pytest.raises(utils.ConnectionTimeoutError):
        utils.wait_for_server('localhost', utils.get_available_port(), 2)


def test_port_functions():
    assert not utils.port_in_use(utils.get_available_port())


def test_pythonnet_py4j_comtypes_installed():
    assert utils.is_pythonnet_installed()
    assert utils.is_py4j_installed()
    if IS_WINDOWS:
        assert utils.is_comtypes_installed()


def test_check_dot_net_config():
    base = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dotnet_config')

    # create the .config file
    exe = os.path.join(base, 'no_config_exists.exe')
    cfg = exe + '.config'
    assert os.path.isfile(exe)
    assert not os.path.isfile(cfg)
    val, msg = utils.check_dot_net_config(exe)
    assert val == 1
    assert msg.startswith('The library appears to be from a .NET Framework version < 4.0')
    assert os.path.isfile(exe + '.config')

    # the useLegacyV2RuntimeActivationPolicy was already enabled
    val, msg = utils.check_dot_net_config(exe)
    assert val == 0
    assert msg == 'The useLegacyV2RuntimeActivationPolicy property is enabled'

    os.remove(cfg)

    # the useLegacyV2RuntimeActivationPolicy was set to false
    exe = os.path.join(base, 'set_to_false.exe')
    val, msg = utils.check_dot_net_config(exe)
    assert val == -1
    assert 'False' in msg

    # the startup element does not exist, it gets inserted
    exe = os.path.join(base, 'startup_element_does_not_exist.exe')
    cfg = exe + '.config'
    cfg_string = """<?xml version ="1.0"?>
<configuration>
    <something>7</something>
</configuration>
"""
    with open(cfg, 'w') as f:
        f.write(cfg_string)
    val, msg = utils.check_dot_net_config(exe)
    assert val == 1
    assert msg.startswith('Added')
    root = ET.parse(cfg).getroot()
    assert root.find('something').text == '7'
    assert root.find('startup').attrib['useLegacyV2RuntimeActivationPolicy'].lower() == 'true'
    os.remove(cfg)

    # the config file exists but it is not a valid XML file
    exe = os.path.join(base, 'invalid_xml.exe')
    val, msg = utils.check_dot_net_config(exe)
    assert val == -1
    assert msg.startswith('Invalid XML file')

    # the config file exists but the root tag is not <configuration>
    exe = os.path.join(base, 'root_tag_is_not_configuration.exe')
    val, msg = utils.check_dot_net_config(exe)
    assert val == -1
    assert msg.startswith('The root tag in')


def test_get_com_info():
    info = utils.get_com_info()
    if IS_WINDOWS:
        assert len(info) > 0
        for value in info.values():
            assert 'ProgID' in value
            assert 'Version' not in value
    else:
        assert len(info) == 0

    info = utils.get_com_info('Version')
    if IS_WINDOWS:
        assert len(info) > 0
        for value in info.values():
            assert 'ProgID' in value
            assert 'Version' in value
    else:
        assert len(info) == 0
