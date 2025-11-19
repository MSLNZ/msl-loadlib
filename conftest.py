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
IS_MAC_ARM64 = IS_MAC and platform.machine() == "arm64"


def has_labview_runtime(*, x86: bool) -> bool:
    """Check if a LabVIEW Run-Time Engine >= 2017 is installed."""
    root = Path("C:/Program Files (x86)") if x86 else Path("C:/Program Files")
    root = root / "National Instruments" / "Shared" / "LabVIEW Run-Time"
    if not root.is_dir():
        return False
    # cSpell: ignore lvrt
    return any(int(folder.name) >= MIN_LABVIEW_RUNTIME and (folder / "lvrt.dll").is_file() for folder in root.iterdir())


MIN_LABVIEW_RUNTIME = 2017
HAS_32BIT_LABVIEW_RUNTIME = has_labview_runtime(x86=True)
HAS_64BIT_LABVIEW_RUNTIME = has_labview_runtime(x86=False)


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
    if not IS_PYTHON_64BIT or IS_MAC_ARM64:
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
    if IS_MAC_ARM64:
        pytest.skip("ignore on macOS arm64")


def no_labview64() -> None:
    """Skip doctest if an appropriate 64-bit LabVIEW Run-Time Engine is not installed."""
    if not HAS_64BIT_LABVIEW_RUNTIME:
        pytest.skip("requires 64-bit LabVIEW Run-Time Engine")


def no_labview32() -> None:
    """Skip doctest if an appropriate 32-bit LabVIEW Run-Time Engine is not installed."""
    if not HAS_32BIT_LABVIEW_RUNTIME:
        pytest.skip("requires 32-bit LabVIEW Run-Time Engine")


def no_pythonnet() -> None:
    """Skip doctest if pythonnet is not installed."""
    if clr is None:
        pytest.skip("pythonnet is not installed/supported on this platform")


def win32_github_actions() -> None:
    """Skip doctest if using a Windows running on GitHub Actions."""
    if IS_WINDOWS and os.getenv("GITHUB_ACTIONS") == "true":
        pytest.skip("flaky test on Windows and GHA")


@pytest.fixture(autouse=True)
def doctest_skipif(doctest_namespace: dict[str, Callable[[], None]]) -> None:
    """Inject skipif conditions for doctest."""
    doctest_namespace.update(
        {
            "SKIP_IF_32BIT": bit32,
            "SKIP_IF_64BIT": bit64,
            "SKIP_IF_MACOS": is_mac,
            "SKIP_IF_MACOS_ARM64": mac_arm64,
            "SKIP_IF_NO_LABVIEW32": no_labview32,
            "SKIP_IF_NO_LABVIEW64": no_labview64,
            "SKIP_IF_NO_PYTHONNET": no_pythonnet,
            "SKIP_IF_NOT_WINDOWS": not_windows,
            "SKIP_IF_WINDOWS_GITHUB_ACTIONS": win32_github_actions,
            "SKIP_README_ALL": readme_all,
            "SKIP_README_COM": readme_com,
            "SKIP_README_DOTNET": readme_dotnet,
        }
    )


skipif_no_comtypes = pytest.mark.skipif(not IS_WINDOWS, reason="comtypes is only supported on Windows")
skipif_no_pythonnet = pytest.mark.skipif(clr is None, reason="pythonnet is not installed/supported on this platform")
skipif_no_server32 = pytest.mark.skipif(IS_MAC, reason="32-bit server does not exist")
skipif_not_windows = pytest.mark.skipif(not IS_WINDOWS, reason="not Windows")

xfail_windows_ga = pytest.mark.xfail(
    IS_WINDOWS and os.getenv("GITHUB_ACTIONS") == "true", reason="flaky test on Windows and GHA"
)
