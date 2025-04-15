import os
import shutil
import socket
import sys
import tempfile
from xml.etree import ElementTree

import pytest

from conftest import IS_MACOS_ARM64
from conftest import skipif_not_windows
from msl.loadlib import utils
from msl.loadlib.constants import IS_WINDOWS


def test_timeout():
    with pytest.raises(utils.ConnectionTimeoutError):
        utils.wait_for_server("localhost", utils.get_available_port(), 2)


def test_port_functions():
    port = utils.get_available_port()
    assert not utils.is_port_in_use(port)
    with socket.socket() as sock:
        sock.bind(("", port))
        sock.listen(1)
        assert utils.is_port_in_use(port)
    assert not utils.is_port_in_use(port)


@pytest.mark.skipif(IS_MACOS_ARM64, reason="macOS and arm64")
def test_is_pythonnet_installed():
    assert utils.is_pythonnet_installed()


def test_is_py4j_installed():
    assert utils.is_py4j_installed()


def test_is_comtypes_installed():
    if IS_WINDOWS:
        assert utils.is_comtypes_installed()
    else:
        assert not utils.is_comtypes_installed()


def test_check_dot_net_config():
    base = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dotnet_config")

    # create the .config file
    exe = os.path.join(base, "no_config_exists.exe")
    cfg = f"{exe}.config"
    assert os.path.isfile(exe)
    assert not os.path.isfile(cfg)
    val, msg = utils.check_dot_net_config(exe)
    assert val == 1
    assert msg.startswith("The library appears to be from a .NET Framework version < 4.0")
    assert os.path.isfile(f"{exe}.config")

    # the useLegacyV2RuntimeActivationPolicy was already enabled
    val, msg = utils.check_dot_net_config(exe)
    assert val == 0
    assert msg == "The useLegacyV2RuntimeActivationPolicy property is enabled"

    os.remove(cfg)

    # the useLegacyV2RuntimeActivationPolicy was set to false
    exe = os.path.join(base, "set_to_false.exe")
    val, msg = utils.check_dot_net_config(exe)
    assert val == -1
    assert 'is "false"' in msg

    # the startup element does not exist, it gets inserted
    exe = os.path.join(base, "startup_element_does_not_exist.exe")
    cfg = f"{exe}.config"
    cfg_string = """<?xml version ="1.0"?>
<configuration>
    <something>7</something>
</configuration>
"""
    with open(cfg, mode="wt") as f:
        f.write(cfg_string)
    val, msg = utils.check_dot_net_config(exe)
    assert val == 1
    assert msg.startswith("Added")
    root = ElementTree.parse(cfg).getroot()
    assert root.find("something").text == "7"
    assert root.find("startup").attrib["useLegacyV2RuntimeActivationPolicy"].lower() == "true"
    os.remove(cfg)

    # the config file exists, but it is not a valid XML file
    exe = os.path.join(base, "invalid_xml.exe")
    val, msg = utils.check_dot_net_config(exe)
    assert val == -1
    assert msg.startswith("Invalid XML file")

    # the config file exists but the root tag is not <configuration>
    exe = os.path.join(base, "root_tag_is_not_configuration.exe")
    val, msg = utils.check_dot_net_config(exe)
    assert val == -1
    assert msg.startswith("The root tag in")


def test_get_com_info():
    info = utils.get_com_info()
    if IS_WINDOWS:
        assert len(info) > 0
        for value in info.values():
            assert "ProgID" in value
            assert "Version" not in value
    else:
        assert len(info) == 0

    info = utils.get_com_info("Version")
    if IS_WINDOWS:
        assert len(info) > 0
        for value in info.values():
            assert "ProgID" in value
            assert "Version" in value
    else:
        assert len(info) == 0


@skipif_not_windows
def test_generate_com_wrapper():
    import comtypes.client
    from msl.loadlib import LoadLibrary

    expected_mod_names = [
        "comtypes.gen.SHDocVw",
        "comtypes.gen._EAB22AC0_30C1_11CF_A7EB_0000C05BAE0B_0_1_1",
    ]

    out_dir = os.path.join(tempfile.gettempdir(), "msl-loadlib-com-wrapper")

    def cleanup():
        for n in expected_mod_names:
            sys.modules.pop(n, None)
        shutil.rmtree(out_dir)

    # comtypes is buggy and sometimes, at random, the following exception is raised
    #   OSError: [WinError -2147467259] Unspecified error
    # when generating the wrapper
    # therefore we
    def run():
        assert comtypes.client.gen_dir.endswith("site-packages\\comtypes\\gen")

        # do not want to save any files in the site-packages/comtypes/gen directory
        # when the LoadLibrary class is called
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)
        cached_gen_dir = comtypes.client.gen_dir
        comtypes.client.gen_dir = out_dir
        com = LoadLibrary("InternetExplorer.Application.1", "com")
        comtypes.client.gen_dir = cached_gen_dir
        cleanup()

        assert comtypes.client.gen_dir.endswith("site-packages\\comtypes\\gen")

        items = [
            "InternetExplorer.Application.1",  # ProgID
            "{0002DF01-0000-0000-C000-000000000046}",  # CLSID
            "shdocvw.dll",  # type library file
            ["{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}", 1, 1],  # [guid, major, minor]
            com,  # LoadLibrary object
            com.lib,  # a COM pointer instance
        ]
        for item in items:
            # make sure that each iteration through this loop generates a new
            # 'mod' object and comtypes does not load the object from the
            # previous loop iteration
            assert not os.path.isdir(out_dir)
            for name in expected_mod_names:
                assert name not in sys.modules

            mod = utils.generate_com_wrapper(item, out_dir=out_dir)
            assert mod.__name__ == expected_mod_names[0]
            assert mod.IWebBrowser2
            for name in expected_mod_names:
                filename = name.split(".")[2] + ".py"
                assert os.path.isfile(os.path.join(out_dir, filename))

            cleanup()

        assert comtypes.client.gen_dir.endswith("site-packages\\comtypes\\gen")

        with pytest.raises(OSError):
            utils.generate_com_wrapper("progid.does.not.exist")

        assert comtypes.client.gen_dir.endswith("site-packages\\comtypes\\gen")

        # a non-LoadLib object should still raise an error
        for obj in [dict(), None, True]:
            with pytest.raises((AttributeError, TypeError)):
                utils.generate_com_wrapper(obj)

        assert comtypes.client.gen_dir.endswith("site-packages\\comtypes\\gen")

    try:
        run()
    except (WindowsError, OSError) as e:
        msg = str(e)
        if msg.endswith("-2147467259] Unspecified error"):
            pytest.xfail(msg)
        else:
            raise
