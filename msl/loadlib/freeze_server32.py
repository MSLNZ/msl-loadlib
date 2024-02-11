"""
Create a server for
`inter-process communication <https://en.wikipedia.org/wiki/Inter-process_communication>`_.
"""
from __future__ import annotations

import os
import sys
from importlib import import_module
from subprocess import check_call
from tempfile import TemporaryDirectory
from typing import Iterable
from urllib.request import urlopen

from msl import loadlib
from msl.loadlib import constants
from msl.loadlib import version_info


# When freezing for a new release, use
# Windows: imports=['msl.examples.loadlib', 'comtypes', 'pythonnet']
# Linux: imports=['msl.examples.loadlib']


def main(*,
         spec: str | None = None,
         dest: str | None = None,
         imports: str | Iterable[str] | None = None,
         data: str | Iterable[str] | None = None,
         skip_32bit_check: bool = False) -> None:
    """Create a frozen server.

    This function should be run using a 32-bit Python interpreter with
    `PyInstaller`_ installed.

    .. versionchanged:: 0.5
       Added the `requires_pythonnet` and `requires_comtypes` arguments.

    .. versionchanged:: 0.10
       Added the `dest` argument.

    .. versionchanged:: 1.0
       Removed the `requires_pythonnet` and `requires_comtypes` arguments.
       Added the `imports`, `data` and `skip_32bit_check` arguments.

    .. _PyInstaller: https://www.pyinstaller.org/

    :param spec: The path to a :ref:`spec file <using spec files>` to use to
        create the frozen server.
    :param dest: The destination directory to save the server to. Default is
        the current directory.
    :param imports: The names of additional modules and packages that must be
        importable on the server.
    :param data: The path(s) to additional data files, or directories containing
        data files, to be added to the frozen server. Each value should be in
        the form `source:dest_dir`, where `:dest_dir` is optional. `source` is
        the path to a file (or a directory of files) to add. `dest_dir` is an
        optional destination directory, relative to the top-level directory of
        the frozen server, to add the file(s) to. If `dest_dir` is not specified,
        the file(s) will be added to the top-level directory of the server.
    :param skip_32bit_check: In the rare situation that you want to create a
        frozen 64-bit server, you can set this value to :data:`True` which skips
        the requirement that a 32-bit version of Python must be used to create
        the server. Before you create a 64-bit server, decide if
        :ref:`msl-loadlib-mock-connection` is a better solution for your
        application.

    .. attention::
        If a value for `spec` is specified, then `imports` nor `data` may be
        specified.
    """
    if not skip_32bit_check and constants.IS_PYTHON_64BIT:
        msg = ''
        if sys.argv:
            if sys.argv[0].endswith('freeze32'):
                msg = ('\nIf you want to create a 64-bit server, you may '
                       'include the\n--skip-32bit-check flag '
                       'to ignore this requirement.')
            else:
                msg = ('\nIf you want to create a 64-bit server, you may '
                       'set the argument\nskip_32bit_check=True '
                       'to ignore this requirement.')
        print(f'Must freeze the server using a 32-bit version of Python.{msg}',
              file=sys.stderr)
        return

    try:
        from PyInstaller import __version__ as pyinstaller_version  # noqa: PyInstaller is not a dependency
    except ImportError:
        print('PyInstaller must be installed to create the server, run:\n'
              'pip install pyinstaller', file=sys.stderr)
        return

    if spec and (imports or data):
        print('Cannot specify a spec file and imports/data', file=sys.stderr)
        return

    here = os.path.abspath(os.path.dirname(__file__))

    if dest is not None:
        dist_path = os.path.abspath(dest)
    else:
        dist_path = os.getcwd()

    tmp_dir = TemporaryDirectory(ignore_cleanup_errors=True)
    work_path = tmp_dir.name
    server_path = os.path.join(dist_path, constants.SERVER_FILENAME)

    # Specifically invoke pyinstaller in the context of the current python interpreter.
    # This fixes the issue where the blind `pyinstaller` invocation points to a 64-bit version.
    cmd = [sys.executable, '-m', 'PyInstaller',
           '--distpath', dist_path,
           '--workpath', work_path,
           '--noconfirm',
           '--clean']

    if spec is None:
        cmd.extend(['--specpath', work_path,
                    '--python-option', 'u'])

        if constants.IS_WINDOWS:
            cmd.extend(['--version-file', _create_version_info_file(work_path)])

        cmd.extend([
            '--name', constants.SERVER_FILENAME,
            '--onefile',
        ])

        if imports:
            if isinstance(imports, str):
                imports = [imports]

            sys.path.append(os.getcwd())

            missing = []
            for module in imports:
                try:
                    import_module(module)
                except ImportError:
                    missing.append(module)
                else:
                    cmd.extend(['--hidden-import', module])

            if missing:
                print(f'The following modules cannot be imported: '
                      f'{" ".join(missing)}\n'
                      f'Cannot freeze the server', file=sys.stderr)
                return

        cmd.extend(_get_standard_modules())

        if data:
            major, *rest = pyinstaller_version.split('.')
            sep = os.pathsep if int(major) < 6 else ':'

            if isinstance(data, str):
                data = [data]

            for item in data:
                s = item.split(':')
                if len(s) == 1:
                    src = s[0]
                    dst = '.'
                elif len(s) == 2:
                    src = s[0]
                    dst = s[1] or '.'
                else:
                    print(f'Invalid data format {item!r}', file=sys.stderr)
                    return

                src = os.path.abspath(src)
                if not os.path.exists(src):
                    print(f'Cannot find {src!r}', file=sys.stderr)
                    return

                cmd.extend(['--add-data', f'{src}{sep}{dst}'])

        cmd.append(os.path.join(here, 'start_server32.py'))
    else:
        cmd.append(spec)

    check_call(cmd)

    # maybe create the .NET Framework config file
    if imports and ('pythonnet' in imports):
        loadlib.utils.check_dot_net_config(server_path)

    print(f'Server saved to {server_path}')
    return 0


def _get_standard_modules() -> list[str]:
    """
    Returns a list of standard python modules to include and exclude in the
    frozen application.

    PyInstaller does not automatically bundle all the standard Python modules
    into the frozen application. This method parses the 'docs.python.org'
    website for the list of standard Python modules that are available.

    The 'pyinstaller --exclude-module' option ensures that the module is
    excluded from the frozen application.

    The 'pyinstaller --hidden-import' option ensures that the module is included
    into the frozen application (only if the module is available for the operating
    system that is running this script).

    :return: A list of modules to be included and excluded.
    """
    # the frozen application is not meant to create GUIs or to add
    # support for building and installing Python modules
    ignore_list = [
        '__main__',
        'distutils',
        'ensurepip',
        'idlelib',
        'lib2to3',
        'test',
        'tkinter',
        'turtle'
    ]

    # some modules are platform specific and got a
    #   RecursionError: maximum recursion depth exceeded
    # when running this script with PyInstaller 3.3 installed
    if constants.IS_WINDOWS:
        os_ignore_list = ['(Unix)', '(Linux)', '(Linux, FreeBSD)']
    elif constants.IS_LINUX:
        os_ignore_list = ['(Windows)']
    elif constants.IS_MAC:
        os_ignore_list = ['(Windows)', '(Linux)', '(Linux, FreeBSD)']
    else:
        os_ignore_list = []

    modules = []
    url = f'https://docs.python.org/{sys.version_info.major}.{sys.version_info.minor}/py-modindex.html'
    for s in urlopen(url).read().decode().split('#module-')[1:]:
        m = s.split('"><code')
        add_module = True
        for x in os_ignore_list:
            if x in m[1]:
                ignore_list.append(m[0])
                add_module = False
                break
        if add_module:
            modules.append(m[0])

    included_modules, excluded_modules = [], []
    for module in modules:
        include_module = True
        for mod in ignore_list:
            if module.startswith(mod):
                excluded_modules.extend(['--exclude-module', module])
                include_module = False
                break
        if include_module:
            included_modules.extend(['--hidden-import', module])
    return included_modules + excluded_modules


def _create_version_info_file(root_dir: str) -> str:
    """Create the version info file for Windows.

    :param root_dir: The directory to save the version file to.
    :return: The filename of the version file.
    """
    text = f"""# UTF-8
#
# For more details about fixed file info 'ffi' see:
# https://docs.microsoft.com/en-us/windows/win32/api/verrsrc/ns-verrsrc-vs_fixedfileinfo
# For language and charset parameters see:
# https://docs.microsoft.com/en-us/windows/win32/menurc/stringfileinfo-block
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_info.major}, {version_info.minor}, {version_info.micro}, 0),
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
        [StringStruct('CompanyName', '{loadlib.__author__}'),
        StringStruct('FileDescription', 'Access a 32-bit library from 64-bit Python'),
        StringStruct('FileVersion', '{version_info.major}.{version_info.minor}.{version_info.micro}.0'),
        StringStruct('InternalName', '{constants.SERVER_FILENAME}'),
        StringStruct('LegalCopyright', '\xc2{loadlib.__copyright__}'),
        StringStruct('OriginalFilename', '{constants.SERVER_FILENAME}'),
        StringStruct('ProductName', 'Python'),
        StringStruct('ProductVersion', '{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}.0')])
      ]), 
    VarFileInfo([VarStruct('Translation', [0, 1200])])
  ]
)
"""
    filename = 'file_version_info.txt'
    with open(os.path.join(root_dir, filename), mode='wt') as fp:
        fp.write(text)
    return filename


def _cli() -> None:
    """Main entry point of the console script."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Create a frozen server for msl-loadlib.',
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        '-s', '--spec',
        help='the path to a PyInstaller .spec file'
    )
    parser.add_argument(
        '-d', '--dest',
        help='the destination directory to save the server to\n'
             '(Default is the current directory)'
    )
    parser.add_argument(
        '-i', '--imports',
        nargs='*',
        help='the names of modules that must be importable on the server\n'
             'Examples:\n'
             '  --imports msl.examples.loadlib\n'
             '  --imports mypackage numpy'
    )
    parser.add_argument(
        '-D', '--data',
        nargs='*',
        help='additional data files to bundle with the server -- the\n'
             'format is "source:dest_dir", where "source" is the path\n'
             'to a file (or a directory of files) to add and "dest_dir"\n'
             'is an optional destination directory, relative to the\n'
             'top-level directory of the frozen server, to add the\n'
             'file(s) to. If dest_dir is not specified, the file(s)\n'
             'will be added to the top-level directory of the server.\n'
             'Examples:\n'
             '  --data mydata\n'
             '  --data mydata/lib1.dll mydata/bin/lib2.dll:bin\n'
             '  --data mypackage/lib32.dll:mypackage'
    )

    parser.add_argument(
        '--skip-32bit-check',
        action='store_true',
        help='in the rare situation that you want to create a frozen\n'
             '64-bit server, you can include this flag which skips the\n'
             'requirement that a 32-bit version of Python must be used\n'
             'to create the server.'
    )

    args = parser.parse_args(sys.argv[1:])

    sys.exit(
        main(
            spec=args.spec,
            dest=args.dest,
            imports=args.imports,
            data=args.data,
            skip_32bit_check=args.skip_32bit_check,
        )
    )
