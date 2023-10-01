"""
Version information.
"""
from __future__ import annotations

from typing import NamedTuple

__all__: list[str] = ['__version__', 'version_info']

__version__: str = '1.0.0.dev0'


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: str


if __version__.endswith('dev0'):
    from importlib.metadata import version, PackageNotFoundError
    try:
        __version__ = version('msl-loadlib')
    except PackageNotFoundError:
        pass

major, minor, micro, *releaselevel = __version__.split('.')

version_info: VersionInfo = VersionInfo(
    int(major), int(minor), int(micro), ''.join(releaselevel) or 'final')
"""Contains the version information as a (major, minor, micro, releaselevel) tuple."""
