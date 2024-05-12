"""
Project information.
"""
from __future__ import annotations

from typing import NamedTuple

from ._version import __version__
from ._version import version_tuple

__all__: list[str] = [
    '__author__',
    '__copyright__',
    '__version__',
    'version_info',
]

__author__: str = 'Measurement Standards Laboratory of New Zealand'
__copyright__: str = f'\xa9 2017 - 2024, {__author__}'


class VersionInfo(NamedTuple):
    """Contains the version information as a
    (major, minor, micro, releaselevel) named tuple."""
    major: int
    minor: int
    micro: int
    releaselevel: str


major, minor, micro, *releaselevel = version_tuple
release_level = ''.join(releaselevel) or 'final'

version_info: VersionInfo = VersionInfo(major, minor, micro, release_level)
