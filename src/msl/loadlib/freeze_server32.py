"""Create a 32-bit server for [inter-process communication]{:target="_blank"}.

**Example:**
```python
from msl.loadlib import freeze_server32
freeze_server32.main(imports="numpy")
```

!!! note
    There is also a [command-line utility][refreeze-cli] to create a new server.

[inter-process communication]: https://en.wikipedia.org/wiki/Inter-process_communication
"""

from __future__ import annotations

import os
import sys
from importlib import import_module
from pathlib import Path
from shutil import copy
from subprocess import check_call
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING
from urllib.request import urlopen

from .__about__ import __author__, __copyright__, version_tuple
from ._constants import IS_LINUX, IS_MAC, IS_PYTHON_64BIT, IS_WINDOWS, server_filename
from .utils import check_dot_net_config

if TYPE_CHECKING:
    from collections.abc import Iterable

# Command to run when freezing the server for a new release
#
# Windows: freeze32 --imports msl.examples.loadlib comtypes pythonnet
# Linux: freeze32 --imports msl.examples.loadlib


def main(  # noqa: C901, PLR0912, PLR0913, PLR0915
    *,
    data: str | Iterable[str] | None = None,
    dest: str | None = None,
    imports: str | Iterable[str] | None = None,
    keep_spec: bool = False,
    keep_tk: bool = False,
    skip_32bit_check: bool = False,
    spec: str | None = None,
) -> None:
    """Create a frozen server.

    This function should be run using a 32-bit Python interpreter with
    [PyInstaller](https://www.pyinstaller.org/){:target="_blank"} installed.

    Args:
        data: The path(s) to additional data files, or directories containing
            data files, to be added to the frozen server. Each value should be in
            the form `source:dest_dir`, where `:dest_dir` is optional. `source` is
            the path to a file (or a directory of files) to add. `dest_dir` is an
            optional destination directory, relative to the top-level directory of
            the frozen server, to add the file(s) to. If `dest_dir` is not specified,
            the file(s) will be added to the top-level directory of the server.
        dest: The destination directory to save the server to. Default is
            the current working directory.
        imports: The names of additional modules and packages that must be
            importable on the server.
        keep_spec: By default, the `.spec` file that is created (during the freezing
            process) is deleted. Setting this value to `True` will keep the `.spec` file,
            so that it may be modified and then passed as the value to the `spec` parameter.
        keep_tk: By default, the [tkinter][]{:target="_blank"} package is excluded from the
            server. Setting this value to `True` will bundle `tkinter` with the server.
        skip_32bit_check: In the rare situation that you want to create a
            frozen 64-bit server, you can set this value to `True` which skips
            the requirement that a 32-bit version of Python must be used to create
            the server. Before you create a 64-bit server, decide if
            [mocking][faq-mock] the connection is a better solution for your
            application.
        spec: The path to a [spec]{:target="_blank"} file to use to create the frozen server.
            [spec]: https://pyinstaller.org/en/stable/spec-files.html#using-spec-files

            !!! attention
                If a value for `spec` is specified, then `imports` or `data` cannot be specified.
    """
    if not skip_32bit_check and IS_PYTHON_64BIT:
        msg = ""
        if sys.argv:
            if sys.argv[0].endswith("freeze32"):
                msg = (
                    "\nIf you want to create a 64-bit server, you may "
                    "include the\n--skip-32bit-check flag "
                    "to ignore this requirement."
                )
            else:
                msg = (
                    "\nIf you want to create a 64-bit server, you may "
                    "set the argument\nskip_32bit_check=True "
                    "to ignore this requirement."
                )
        print(f"ERROR! Must freeze the server using a 32-bit version of Python.{msg}", file=sys.stderr)
        return

    try:
        from PyInstaller import (  # type: ignore[import-untyped] # pyright: ignore[reportMissingModuleSource]  # noqa: PLC0415
            __version__ as pyinstaller_version,
        )
    except ImportError:
        print(
            "ERROR! PyInstaller must be installed to create the server, run:\npip install pyinstaller", file=sys.stderr
        )
        return

    if spec and (imports or data):
        print("ERROR! Cannot specify a spec file and imports/data", file=sys.stderr)
        return

    here = Path(__file__).parent
    dist_path = Path(dest) if dest is not None else Path.cwd()
    server_path = dist_path / server_filename

    tmp_dir = (
        TemporaryDirectory(ignore_cleanup_errors=True) if sys.version_info[:2] >= (3, 10) else TemporaryDirectory()
    )
    work_path = Path(tmp_dir.name)

    # Specifically invoke pyinstaller in the context of the current python interpreter.
    # This fixes the issue where the blind `pyinstaller` invocation points to a 64-bit version.
    cmd: list[str] = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--distpath",
        str(dist_path),
        "--workpath",
        str(work_path),
        "--noconfirm",
        "--clean",
    ]

    if spec is None:
        cmd.extend(["--specpath", str(work_path), "--python-option", "u"])

        if IS_WINDOWS:
            cmd.extend(["--version-file", _create_version_info_file(work_path)])

        cmd.extend(
            [
                "--name",
                server_filename,
                "--onefile",
            ]
        )

        if imports:
            if isinstance(imports, str):
                imports = [imports]

            sys.path.append(str(Path.cwd()))

            missing: list[str] = []
            for module in imports:
                try:
                    _ = import_module(module)
                except ImportError:  # noqa: PERF203
                    missing.append(module)
                else:
                    cmd.extend(["--hidden-import", module])

            if missing:
                print(
                    f"ERROR! The following modules cannot be imported: {' '.join(missing)}\nCannot freeze the server",
                    file=sys.stderr,
                )
                return

        cmd.extend(_get_standard_modules(keep_tk=keep_tk))

        if data:
            major, *_ = pyinstaller_version.split(".")
            sep = os.pathsep if int(major) < 6 else ":"  # noqa: PLR2004

            if isinstance(data, str):
                data = [data]

            for item in data:
                s = item.split(":")
                if len(s) == 1:
                    src = s[0]
                    dst = "."
                elif len(s) == 2:  # noqa: PLR2004
                    src = s[0]
                    dst = s[1] or "."
                else:
                    print(f"ERROR! Invalid data format {item!r}", file=sys.stderr)
                    return

                source = Path(src).resolve()
                if not source.exists():
                    print(f"ERROR! Cannot find {source}", file=sys.stderr)
                    return

                cmd.extend(["--add-data", f"{source}{sep}{dst}"])

        cmd.append(str(here / "start_server32.py"))
    else:
        cmd.append(spec)

    _ = check_call(cmd)  # noqa: S603

    # maybe create the .NET Framework config file
    if imports and ("pythonnet" in imports):
        _ = check_dot_net_config(server_path)

    if keep_spec and not spec:
        print(f"The following files were saved to {dist_path}\n  {server_filename}")

        if Path(f"{server_path}.config").is_file():
            print(f"  {server_path.name}.config")

        spec_file = "server32.spec"
        _ = copy(work_path / f"{server_filename}.spec", dist_path / spec_file)
        print(f"  {spec_file}")

        if IS_WINDOWS:
            file_version_info = "file_version_info.txt"
            _ = copy(work_path / file_version_info, dist_path)
            print(f"  {file_version_info}  (required by the {spec_file} file)")
    else:
        print(f"Server saved to {server_path}")


def _get_standard_modules(*, keep_tk: bool) -> list[str]:  # noqa: C901, PLR0912
    """Returns a list of standard python modules to include and exclude in the frozen application.

    PyInstaller does not automatically bundle all the standard Python modules
    into the frozen application. This method parses the 'docs.python.org'
    website for the list of standard Python modules that are available.

    The 'pyinstaller --exclude-module' option ensures that the module is
    excluded from the frozen application.

    The 'pyinstaller --hidden-import' option ensures that the module is included
    into the frozen application (only if the module is available for the operating
    system that is running this script).
    """
    # The frozen application is not meant to create GUIs or to add
    # support for building and installing Python modules.
    #
    # PyInstaller wants to include distutils via hook-distutils.py,
    # and modifying hooks can only be done with a .spec file.
    # So that's why distutils is not in the ignore_list.

    ignore_list = [
        "__main__",
        "ensurepip",
        "idlelib",
        "lib2to3",
        "test",
        "turtle",
    ]

    if not keep_tk:
        ignore_list.extend(["tkinter", "_tkinter"])

    # some modules are platform specific and got a
    #   RecursionError: maximum recursion depth exceeded
    # when running this script with PyInstaller 3.3 installed
    if IS_WINDOWS:
        os_ignore_list = ["(Unix)", "(Linux)", "(Linux, FreeBSD)"]
    elif IS_LINUX:
        os_ignore_list = ["(Windows)"]
    elif IS_MAC:
        os_ignore_list = ["(Windows)", "(Linux)", "(Linux, FreeBSD)"]
    else:
        os_ignore_list = []

    modules: list[str] = []
    for s in urlopen("https://docs.python.org/3/py-modindex.html").read().decode().split("#module-")[1:]:
        m = s.split('"><code')
        add_module = True
        for x in os_ignore_list:
            if x in m[1]:
                ignore_list.append(m[0])
                add_module = False
                break
        if add_module:
            modules.append(m[0])

    included_modules: list[str] = []
    excluded_modules: list[str] = []
    for module in modules:
        include_module = True
        for mod in ignore_list:
            if module.startswith(mod):
                excluded_modules.extend(["--exclude-module", module])
                include_module = False
                break
        if include_module:
            included_modules.extend(["--hidden-import", module])
    return included_modules + excluded_modules


def _create_version_info_file(root_dir: Path) -> str:
    """Create the version-info file for Windows.

    Args:
        root_dir: The directory to save the version file to.

    Returns:
        The filename of the version file.
    """
    text = f"""# UTF-8
#
# For more details about fixed file info 'ffi' see:
# https://docs.microsoft.com/en-us/windows/win32/api/verrsrc/ns-verrsrc-vs_fixedfileinfo
# For language and charset parameters see:
# https://docs.microsoft.com/en-us/windows/win32/menurc/stringfileinfo-block
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
    StringFileInfo(
      [
      StringTable(
        '000004B0',
        [StringStruct('CompanyName', '{__author__}'),
        StringStruct('FileDescription', 'Access a 32-bit library from 64-bit Python'),
        StringStruct('FileVersion', '{version_tuple[0]}.{version_tuple[1]}.{version_tuple[2]}.0'),
        StringStruct('InternalName', '{server_filename}'),
        StringStruct('LegalCopyright', '\xc2{__copyright__}'),
        StringStruct('OriginalFilename', '{server_filename}'),
        StringStruct('ProductName', 'Python'),
        StringStruct('ProductVersion', '{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}.0')])
      ]),
    VarFileInfo([VarStruct('Translation', [0, 1200])])
  ]
)
"""
    filename = "file_version_info.txt"
    _ = (root_dir / filename).write_text(text)
    return filename


def _cli() -> None:  # pyright: ignore[reportUnusedFunction]
    """Main entry point of the console script."""
    import argparse  # noqa: PLC0415

    parser = argparse.ArgumentParser(
        description="Create a frozen server for msl-loadlib.",
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
    )
    _ = parser.add_argument(
        "-h", "--help", action="help", default=argparse.SUPPRESS, help="Show this help message and exit."
    )
    _ = parser.add_argument("-s", "--spec", help="The path to a PyInstaller .spec file.")
    _ = parser.add_argument(
        "-d", "--dest", help="The destination directory to save the server to.\n(Default is the current directory)"
    )
    _ = parser.add_argument(
        "-i",
        "--imports",
        nargs="*",
        help=(
            "The names of modules that must be importable on the server.\n"
            "Examples:\n"
            "  --imports msl.examples.loadlib\n"
            "  --imports mypackage numpy"
        ),
    )
    _ = parser.add_argument(
        "-D",
        "--data",
        nargs="*",
        help=(
            "Additional data files to bundle with the server -- the\n"
            'format is "source:dest_dir", where "source" is the path\n'
            'to a file (or a directory of files) to add and "dest_dir"\n'
            "is an optional destination directory, relative to the\n"
            "top-level directory of the frozen server, to add the\n"
            "file(s) to. If dest_dir is not specified, the file(s)\n"
            "will be added to the top-level directory of the server.\n"
            "Examples:\n"
            "  --data mydata\n"
            "  --data mydata/lib1.dll mydata/bin/lib2.dll:bin\n"
            "  --data mypackage/lib32.dll:mypackage"
        ),
    )
    _ = parser.add_argument(
        "--skip-32bit-check",
        action="store_true",
        help=(
            "In the rare situation that you want to create a frozen\n"
            "64-bit server, you can include this flag which skips the\n"
            "requirement that a 32-bit version of Python must be used\n"
            "to create the server."
        ),
    )
    _ = parser.add_argument(
        "--keep-spec",
        action="store_true",
        help=(
            "By default, the PyInstaller '.spec' file (that is created\n"
            "when the server is frozen) is deleted. Including this\n"
            "flag will keep the '.spec' file, so that it may be modified\n"
            "and then passed as the value to the '--spec' option."
        ),
    )
    _ = parser.add_argument(
        "--keep-tk",
        action="store_true",
        help=(
            "By default, the tkinter module is excluded from the server.\n"
            "Including this flag will bundle tkinter with the server."
        ),
    )

    args = parser.parse_args(sys.argv[1:])

    sys.exit(
        main(  # type: ignore[func-returns-value]
            data=args.data,
            dest=args.dest,
            imports=args.imports,
            keep_spec=args.keep_spec,
            keep_tk=args.keep_tk,
            skip_32bit_check=args.skip_32bit_check,
            spec=args.spec,
        )
    )
