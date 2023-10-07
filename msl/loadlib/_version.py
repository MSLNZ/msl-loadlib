"""
Version information.
"""
from __future__ import annotations

from typing import NamedTuple

__all__: list[str] = ['__version__', '__version_info__']

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

__version_info__: VersionInfo = VersionInfo(
    int(major), int(minor), int(micro), ''.join(releaselevel) or 'final')
