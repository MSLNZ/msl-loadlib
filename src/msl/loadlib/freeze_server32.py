#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create a 32-bit server for inter-process communication with PyInstaller.

This script freezes a small Python program (`start_server32.py`) into a
single executable that can be launched from a 64-bit Python process to
communicate with 32-bit libraries via IPC.

Usage:
    python freeze_server32.py [options]

Example:
    python freeze_server32.py --imports msl.examples.loadlib comtypes pythonnet
"""

from __future__ import annotations

import argparse
import os
import sys
from importlib import import_module
from shutil import copy
from subprocess import check_call
from tempfile import TemporaryDirectory
from typing import Iterable
from urllib.error import URLError
from urllib.request import urlopen

from msl import loadlib
from msl.loadlib import constants
from msl.loadlib import version_tuple

# ------------------------------------------------------------------------------
# main()
# ------------------------------------------------------------------------------

def main(
    *,
    data: str | Iterable[str] | None = None,
    dest: str | None = None,
    imports: str | Iterable[str] | None = None,
    keep_spec: bool = False,
    keep_tk: bool = False,
    skip_32bit_check: bool = False,
    spec: str | None = None,
) -> None:
    """
    Create a frozen server using PyInstaller (must be run under 32-bit Python).

    Args:
      data:   Optional list of "src[:dst]" additional files or directories to bundle.
      dest:   Optional output directory (defaults to cwd).
      imports: Optional list of module names that must be importable at runtime.
      keep_spec: If True, preserve the generated .spec and version file.
      keep_tk: If True, include tkinter in the build.
      skip_32bit_check: If True, allow running under 64-bit Python.
      spec:   Optional path to an existing .spec file (imports/data are ignored).
    """
    # 1) Prevent running under 64-bit Python unless explicitly overridden
    if not skip_32bit_check and constants.IS_PYTHON_64BIT:
        raise RuntimeError(
            "Must freeze the server using a 32-bit Python interpreter.\n"
            "Use --skip-32bit-check to override."
        )

    # 2) Ensure PyInstaller is installed
    try:
        from PyInstaller import __version__ as pyinstaller_version  # noqa: F401
    except ImportError:
        raise RuntimeError("PyInstaller is required: pip install pyinstaller")

    # 3) Prevent mixing spec file with imports/data
    if spec and (imports or data):
        raise ValueError("Cannot specify both --spec and --imports/--data at once")

    here = os.path.abspath(os.path.dirname(__file__))
    dist_path = os.path.abspath(dest) if dest else os.getcwd()

    # 4) Build the base PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--distpath", dist_path,
        "--noconfirm", "--clean",
    ]

    if spec is None:
        # generate fresh build
        cmd += [
            "--workpath", "build",
            "--specpath", "build",
            "--onefile",
            "--name", constants.SERVER_FILENAME,
        ]
        # add version-info on Windows
        if constants.IS_WINDOWS:
            cmd += ["--version-file", _create_version_info_file("build")]
    else:
        # use existing spec
        cmd.append(spec)

    # 5) If building from scratch, add imports, stdlib modules, data, and entry script
    if spec is None:
        _add_imports(cmd, imports)
        cmd += _get_standard_modules(keep_tk)
        _add_data_files(cmd, data)
        cmd.append(os.path.join(here, "start_server32.py"))

    # 6) Execute the freeze inside a TemporaryDirectory (auto-cleaned)
    with TemporaryDirectory() as build_dir:
        if spec is None:
            # update workpath/specpath to point at our temp dir
            _replace_flag_arg(cmd, "--workpath", build_dir)
            _replace_flag_arg(cmd, "--specpath", build_dir)

        check_call(cmd)

        # post-freeze: if pythonnet was bundled, ensure .NET config is set
        if imports and "pythonnet" in (imports if isinstance(imports, list) else [imports]):
            loadlib.utils.check_dot_net_config(
                os.path.join(dist_path, constants.SERVER_FILENAME)
            )

        # preserve spec + version file if requested
        if keep_spec and spec is None:
            _preserve_spec_and_version(build_dir, dist_path)

    print(f"✔ Server binary created at {os.path.join(dist_path, constants.SERVER_FILENAME)}")


# ------------------------------------------------------------------------------
# Helper: Add imports
# ------------------------------------------------------------------------------
def _add_imports(cmd: list[str], imports: str | Iterable[str] | None) -> None:
    """Validate and append --hidden-import flags for each requested module."""
    if not imports:
        return
    modules = [imports] if isinstance(imports, str) else list(imports)
    missing = []
    for mod in modules:
        try:
            import_module(mod)
        except ImportError:
            missing.append(mod)
        else:
            cmd += ["--hidden-import", mod]
    if missing:
        raise RuntimeError("Cannot import modules: " + ", ".join(missing))


# ------------------------------------------------------------------------------
# Helper: Add data files
# ------------------------------------------------------------------------------
def _add_data_files(cmd: list[str], data: str | Iterable[str] | None) -> None:
    """Validate and append --add-data flags for each data specification."""
    if not data:
        return
    items = [data] if isinstance(data, str) else list(data)
    sep = os.pathsep
    for item in items:
        src, *dst = item.split(":", 1)
        dst = dst[0] if dst else ""
        src = os.path.abspath(src)
        if not os.path.exists(src):
            raise FileNotFoundError(f"Data file not found: {src!r}")
        cmd += ["--add-data", f"{src}{sep}{dst}"]


# ------------------------------------------------------------------------------
# Helper: Replace a flag’s argument in the cmd list
# ------------------------------------------------------------------------------
def _replace_flag_arg(cmd: list[str], flag: str, new_arg: str) -> None:
    """Locate flag in cmd and replace its following element with new_arg."""
    if flag in cmd:
        idx = cmd.index(flag) + 1
        cmd[idx] = new_arg


# ------------------------------------------------------------------------------
# Helper: Standard library module inclusion/exclusion
# ------------------------------------------------------------------------------
def _get_standard_modules(keep_tk: bool) -> list[str]:
    """
    Return a list of --hidden-import / --exclude-module flags covering the
    Python standard library, skipping tests, GUI toolkits, etc.
    """
    ignore_prefixes = {
        "__main__", "ensurepip", "idlelib", "lib2to3", "test", "turtle"
    }
    if not keep_tk:
        ignore_prefixes |= {"tkinter", "_tkinter"}

    try:
        url = f"https://docs.python.org/{sys.version_info.major}/py-modindex.html"
        html = urlopen(url, timeout=5).read().decode()
        names = {chunk.split('"><code')[0] for chunk in html.split("#module-")[1:]}
    except (URLError, TimeoutError):
        # offline fallback
        names = {"ctypes", "sys", "os", "subprocess"}

    flags: list[str] = []
    for name in sorted(names):
        if any(name.startswith(pref) for pref in ignore_prefixes):
            flags += ["--exclude-module", name]
        else:
            flags += ["--hidden-import", name]
    return flags


# ------------------------------------------------------------------------------
# Helper: Create Windows version-info file
# ------------------------------------------------------------------------------
def _create_version_info_file(root_dir: str) -> str:
    """
    Generate a file_version_info.txt in root_dir for embedding into the
    Windows executable’s metadata.
    """
    text = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_tuple[0]}, {version_tuple[1]}, {version_tuple[2]}, 0),
    prodvers=({sys.version_info.major}, {sys.version_info.minor}, {sys.version_info.micro}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '000004B0',
        [
          StringStruct('CompanyName', '{loadlib.__author__}'),
          StringStruct('FileDescription', '32-bit IPC server for msl-loadlib'),
          StringStruct('FileVersion', '{version_tuple[0]}.{version_tuple[1]}.{version_tuple[2]}.0'),
          StringStruct('OriginalFilename', '{constants.SERVER_FILENAME}'),
          StringStruct('ProductName', 'msl-loadlib'),
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [0, 1200])])
  ]
)
"""
    filename = "file_version_info.txt"
    path = os.path.join(root_dir, filename)
    with open(path, "w", encoding="utf-8") as fp:
        fp.write(text)
    return path


# ------------------------------------------------------------------------------
# CLI entry point
# ------------------------------------------------------------------------------
def _cli() -> None:
    """Console-script entry point for `freeze32`."""
    parser = argparse.ArgumentParser(
        prog="freeze32",
        description="Freeze a 32-bit IPC server for msl-loadlib"
    )
    parser.add_argument(
        "-s", "--spec",
        help="Use an existing PyInstaller .spec file (ignores --imports/--data)"
    )
    parser.add_argument(
        "-d", "--dest",
        help="Output directory (default: current working directory)"
    )
    parser.add_argument(
        "-i", "--imports", nargs="*",
        help="Additional modules that must be importable at runtime"
    )
    parser.add_argument(
        "-D", "--data", nargs="*",
        help="Additional data files to bundle, format 'src[:dst]'"
    )
    parser.add_argument(
        "--skip-32bit-check", action="store_true",
        help="Allow freezing under 64-bit Python interpreter"
    )
    parser.add_argument(
        "--keep-spec", action="store_true",
        help="Preserve generated .spec and version-info files"
    )
    parser.add_argument(
        "--keep-tk", action="store_true",
        help="Include tkinter in the build"
    )
    args = parser.parse_args()
    sys.exit(main(
        data=args.data,
        dest=args.dest,
        imports=args.imports,
        keep_spec=args.keep_spec,
        keep_tk=args.keep_tk,
        skip_32bit_check=args.skip_32bit_check,
        spec=args.spec,
    ))


if __name__ == "__main__":
    _cli()
