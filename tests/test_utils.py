import shutil
import socket
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from conftest import IS_MAC_ARM64, IS_WINDOWS, skipif_not_windows
from msl.loadlib import ConnectionTimeoutError, LoadLibrary, utils


def test_timeout() -> None:
    with pytest.raises(ConnectionTimeoutError):
        utils.wait_for_server("localhost", utils.get_available_port(), 2)


def test_port_functions() -> None:
    port = utils.get_available_port()
    assert not utils.is_port_in_use(port)
    with socket.socket() as sock:
        sock.bind(("", port))
        sock.listen(1)
        assert utils.is_port_in_use(port)
    assert not utils.is_port_in_use(port)


@pytest.mark.skipif(IS_MAC_ARM64, reason="macOS and arm64")
def test_is_pythonnet_installed() -> None:
    assert utils.is_pythonnet_installed()


def test_is_py4j_installed() -> None:
    assert utils.is_py4j_installed()


def test_is_comtypes_installed() -> None:
    if IS_WINDOWS:
        assert utils.is_comtypes_installed()
    else:
        assert not utils.is_comtypes_installed()


def test_check_dot_net_config() -> None:
    base = Path(__file__).parent / "dotnet_config"

    # create the .config file
    exe = base / "no_config_exists.exe"
    cfg = Path(f"{exe}.config")
    assert exe.is_file()
    assert not cfg.is_file()
    val, msg = utils.check_dot_net_config(exe)
    assert val == 1
    assert msg.startswith("The library appears to be from a .NET Framework version < 4.0")
    assert cfg.is_file()

    # the useLegacyV2RuntimeActivationPolicy was already enabled
    val, msg = utils.check_dot_net_config(exe)
    assert val == 0
    assert msg == "The useLegacyV2RuntimeActivationPolicy property is enabled"

    cfg.unlink()

    # the useLegacyV2RuntimeActivationPolicy was set to false
    exe = base / "set_to_false.exe"
    val, msg = utils.check_dot_net_config(exe)
    assert val == -1
    assert 'is "false"' in msg

    # the startup element does not exist, it gets inserted
    exe = base / "startup_element_does_not_exist.exe"
    cfg = Path(f"{exe}.config")
    cfg_string = """<?xml version ="1.0"?>
<configuration>
    <something>7</something>
</configuration>
"""
    _ = cfg.write_text(cfg_string)
    val, msg = utils.check_dot_net_config(exe)
    assert val == 1
    assert msg.startswith("Added")
    root = ET.parse(cfg).getroot()  # noqa: S314
    something = root.find("something")
    assert something is not None
    assert something.text == "7"
    startup = root.find("startup")
    assert startup is not None
    assert startup.attrib["useLegacyV2RuntimeActivationPolicy"].lower() == "true"
    cfg.unlink()

    # the config file exists, but it is not a valid XML file
    exe = base / "invalid_xml.exe"
    val, msg = utils.check_dot_net_config(exe)
    assert val == -1
    assert msg.startswith("Invalid XML file")

    # the config file exists but the root tag is not <configuration>
    exe = base / "root_tag_is_not_configuration.exe"
    val, msg = utils.check_dot_net_config(exe)
    assert val == -1
    assert msg.startswith("The root tag in")


def test_get_com_info() -> None:
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
def test_generate_com_wrapper() -> None:
    import comtypes.client  # type: ignore[import-untyped] # pyright: ignore[reportMissingTypeStubs]

    expected_mod_names = [
        "comtypes.gen.SHDocVw",
        "comtypes.gen._EAB22AC0_30C1_11CF_A7EB_0000C05BAE0B_0_1_1",
    ]

    out_dir = Path(tempfile.gettempdir()) / "msl-loadlib-com-wrapper"

    def cleanup() -> None:
        for n in expected_mod_names:
            _ = sys.modules.pop(n, None)
        shutil.rmtree(out_dir)

    # comtypes is buggy and sometimes, at random, the following exception is raised
    #   OSError: [WinError -2147467259] Unspecified error
    # when generating the wrapper
    def run() -> None:
        assert isinstance(comtypes.client.gen_dir, str)  # pyright: ignore[reportUnknownMemberType]
        assert comtypes.client.gen_dir.endswith("site-packages\\comtypes\\gen")

        # do not want to save any files in the site-packages/comtypes/gen directory
        # when the LoadLibrary class is called
        out_dir.mkdir(exist_ok=True)
        cached_gen_dir: str = comtypes.client.gen_dir
        comtypes.client.gen_dir = str(out_dir)
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
            assert not out_dir.is_dir()
            for name in expected_mod_names:
                assert name not in sys.modules

            mod = utils.generate_com_wrapper(item, out_dir=out_dir)
            assert mod.__name__ == expected_mod_names[0]
            assert mod.IWebBrowser2
            for name in expected_mod_names:
                filename = name.split(".")[2] + ".py"
                assert (out_dir / filename).is_file()

            cleanup()

        assert comtypes.client.gen_dir.endswith("site-packages\\comtypes\\gen")

        with pytest.raises(OSError):  # noqa: PT011
            _ = utils.generate_com_wrapper("progid.does.not.exist")

        assert comtypes.client.gen_dir.endswith("site-packages\\comtypes\\gen")

        # a non-LoadLib object should still raise an error
        for obj in [{}, None, True]:  # type: ignore[var-annotated] # pyright: ignore[reportUnknownVariableType]
            with pytest.raises((AttributeError, TypeError)):
                _ = utils.generate_com_wrapper(obj)

        assert comtypes.client.gen_dir.endswith("site-packages\\comtypes\\gen")

    try:
        run()
    except OSError as e:
        msg = str(e)
        if msg.endswith("-2147467259] Unspecified error"):
            pytest.xfail(msg)
        else:
            raise
