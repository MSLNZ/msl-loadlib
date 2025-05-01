"""Configuration file for pytest."""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path
from typing import Callable

import pytest

try:
    import clr  # type: ignore[import-untyped]  # pyright: ignore[reportMissingTypeStubs]
except (ImportError, RuntimeError):
    clr = None

from msl.loadlib import IS_PYTHON_64BIT

IS_WINDOWS: bool = sys.platform == "win32"
IS_MAC: bool = sys.platform == "darwin"
IS_MACOS_ARM64 = sys.platform == "darwin" and platform.machine() == "arm64"


def has_labview_runtime() -> bool:
    """Checks if a LabVIEW runtime is installed."""
    root: Path
    if IS_PYTHON_64BIT:
        root = Path(r"C:\Program Files\National Instruments\Shared\LabVIEW Run-Time")
    else:
        root = Path(r"C:\Program Files (x86)\National Instruments\Shared\LabVIEW Run-Time")

    if not root.is_dir():
        return False

    for item in root.iterdir():
        path = root / item / "lvrt.dll"  # cSpell: ignore lvrt
        if path.is_file():
            return True

    return False


def not_windows() -> None:
    """Skip doctest if not Windows."""
    if not IS_WINDOWS:
        pytest.skip("not Windows")


def is_mac() -> None:
    """Skip doctest if macOS."""
    if IS_MAC:
        pytest.skip("is macOS")


def bit64() -> None:
    """Skip doctest if 64-bit Python."""
    if IS_PYTHON_64BIT:
        pytest.skip("requires 32-bit Python")


def bit32() -> None:
    """Skip doctest if 32-bit Python."""
    if not IS_PYTHON_64BIT:
        pytest.skip("requires 64-bit Python")


def readme_all() -> None:
    """Skip all doctest in README."""
    if not IS_PYTHON_64BIT or IS_MACOS_ARM64:
        pytest.skip("skipped all tests")


def readme_dotnet() -> None:
    """Skip from .NET doctest in README."""
    if clr is None:
        pytest.skip("skipped at .NET test")


def readme_com() -> None:
    """Skip from COM doctest in README."""
    if not IS_WINDOWS:
        pytest.skip("skipped at COM test")


def mac_arm64() -> None:
    """Skip doctest if macOS and ARM64."""
    if IS_MACOS_ARM64:
        pytest.skip("ignore on macOS arm64")


def no_labview64() -> None:
    """Skip doctest if a 64-bit LabVIEW Run-Time Engine is not installed."""
    if not (IS_PYTHON_64BIT and has_labview_runtime()):
        pytest.skip("requires 64-bit LabVIEW Run-Time Engine")


def no_labview32() -> None:
    """Skip doctest if a 32-bit LabVIEW Run-Time Engine is not installed."""
    pytest.skip("not checking if 32-bit LabVIEW is installed")


def no_pythonnet() -> None:
    """Skip doctest if pythonnet is not installed."""
    if clr is None:
        pytest.skip("pythonnet is not installed")


def win32_github_actions() -> None:
    """Skip doctest if using a Windows running on GitHub Actions."""
    if IS_WINDOWS and os.getenv("GITHUB_ACTIONS") == "true":
        pytest.skip("flaky test on Windows and GHA")


@pytest.fixture(autouse=True)
def doctest_skipif(doctest_namespace: dict[str, Callable[[], None]]) -> None:
    """Inject skipif conditions for doctest."""
    doctest_namespace["SKIP_IF_WINDOWS_GITHUB_ACTIONS"] = win32_github_actions
    doctest_namespace["SKIP_IF_NOT_WINDOWS"] = not_windows
    doctest_namespace["SKIP_IF_MACOS"] = is_mac
    doctest_namespace["SKIP_IF_MACOS_ARM64"] = mac_arm64
    doctest_namespace["SKIP_IF_64BIT"] = bit64
    doctest_namespace["SKIP_IF_32BIT"] = bit32
    doctest_namespace["SKIP_IF_LABVIEW64_NOT_INSTALLED"] = no_labview64
    doctest_namespace["SKIP_LABVIEW32"] = no_labview32
    doctest_namespace["SKIP_README_DOTNET"] = readme_dotnet
    doctest_namespace["SKIP_README_COM"] = readme_com
    doctest_namespace["SKIP_README_ALL"] = readme_all
    doctest_namespace["SKIP_IF_NO_PYTHONNET"] = no_pythonnet


skipif_no_comtypes = pytest.mark.skipif(not IS_WINDOWS, reason="comtypes is only supported on Windows")
skipif_no_labview_runtime = pytest.mark.skipif(not has_labview_runtime(), reason="requires LabVIEW Run-Time Engine")
skipif_no_pythonnet = pytest.mark.skipif(clr is None, reason="pythonnet is not installed")
skipif_no_server32 = pytest.mark.skipif(IS_MAC, reason="32-bit server does not exist")
skipif_not_windows = pytest.mark.skipif(not IS_WINDOWS, reason="not Windows")

xfail_windows_ga = pytest.mark.xfail(
    IS_WINDOWS and os.getenv("GITHUB_ACTIONS") == "true", reason="flaky test on Windows and GHA"
)
