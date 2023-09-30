"""
Create a 32-bit server to use for
`inter-process communication <https://en.wikipedia.org/wiki/Inter-process_communication>`_.
"""
import os
import sys
from importlib import import_module
from subprocess import check_call
from tempfile import TemporaryDirectory
from urllib.request import urlopen

from msl import loadlib


def main(spec=None, dest=None, packages=None, data=None):
    """Create a frozen 32-bit server.

    This function must be run from a 32-bit Python interpreter with `PyInstaller`_ installed.

    Uses `PyInstaller`_ to create a frozen 32-bit Python executable. This
    executable starts a 32-bit server, :class:`~.server32.Server32`, which
    hosts a Python module that can load a 32-bit library.

    If a value for `spec` is specified, then `packages` or `data` cannot
    be specified.

    .. versionchanged:: 1.0
       Removed the `requires_pythonnet` and `requires_comtypes` arguments.
       Added the `packages` and `data` arguments.

    .. versionchanged:: 0.10
       Added the `dest` argument.

    .. versionchanged:: 0.5
       Added the `requires_pythonnet` and `requires_comtypes` arguments.

    .. _PyInstaller: https://www.pyinstaller.org/

    Parameters
    ----------
    spec : :class:`str`, optional
        The path to a :ref:`spec file <using spec files>` to use to create
        the frozen 32-bit server.
    dest : :class:`str`, optional
        The destination directory to save the 32-bit server to. Default is
        the current directory.
    packages : :class:`str` or :class:`list` of :class:`str`, optional
        The names of additional packages to bundle with the 32-bit server.
    data : :class:`str` or :class:`list` of :class:`str`, optional
        The path(s) to additional data files, or directories containing data
        files, to be added to the frozen 32-bit server. Each value should be
        in the form `source:dest_dir`, where `:dest_dir` is optional. `source`
        is the path to a file (or a directory of files) to add. `dest_dir`
        is an optional destination directory, relative to the top-level
        directory of the frozen 32-bit server, to add the file(s) to. If
        `dest_dir` is not specified, the file(s) will be added to the
        top-level directory of the 32-bit server.
    """
    if loadlib.IS_PYTHON_64BIT:
        print('Must freeze the server using a 32-bit Python interpreter', file=sys.stderr)
        return

    try:
        from PyInstaller import __version__ as pyinstaller_version  # noqa
    except ImportError:
        print('PyInstaller must be installed to create the 32-bit server, run:\n'
              'pip install pyinstaller', file=sys.stderr)
        return

    if spec and (packages or data):
        print('Cannot specify a spec file and packages/data', file=sys.stderr)
        return

    here = os.path.abspath(os.path.dirname(__file__))

    if dest is not None:
        dist_path = os.path.abspath(dest)
    else:
        dist_path = os.getcwd()

    tmp_dir = TemporaryDirectory(ignore_cleanup_errors=True)
    work_path = tmp_dir.name
    server_path = os.path.join(dist_path, loadlib.SERVER_FILENAME)

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

        if loadlib.IS_WINDOWS:
            cmd.extend(['--version-file', _create_version_info_file(work_path)])

        cmd.extend([
            '--name', loadlib.SERVER_FILENAME,
            '--onefile',
            '--hidden-import', 'msl.examples.loadlib',
        ])

        if packages:
            if isinstance(packages, str):
                packages = [packages]

            sys.path.append(os.getcwd())

            missing = []
            for package in packages:
                try:
                    import_module(package)
                except ImportError:
                    missing.append(package)
                else:
                    cmd.extend(['--hidden-import', package])

            if missing:
                print(f'Packages are missing to be able to create the 32-bit server, run:\n'
                      f'pip install {" ".join(missing)}', file=sys.stderr)
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
    if packages and ('pythonnet' in packages or 'clr' in packages):
        loadlib.utils.check_dot_net_config(server_path)

    print(f'Server saved to {server_path}')


def _get_standard_modules():
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

    Returns
    -------
    :class:`list` of :class:`str`
        A list of modules to be included and excluded.
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
    if loadlib.IS_WINDOWS:
        os_ignore_list = ['(Unix)', '(Linux)', '(Linux, FreeBSD)']
    elif loadlib.IS_LINUX:
        os_ignore_list = ['(Windows)']
    elif loadlib.IS_MAC:
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


def _create_version_info_file(root_path):
    text = f"""# UTF-8
#
# For more details about fixed file info 'ffi' see:
# https://docs.microsoft.com/en-us/windows/win32/api/verrsrc/ns-verrsrc-vs_fixedfileinfo
# For language and charset parameters see:
# https://docs.microsoft.com/en-us/windows/win32/menurc/stringfileinfo-block
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({loadlib.version_info.major}, {loadlib.version_info.minor}, {loadlib.version_info.micro}, 0),
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
        StringStruct('FileVersion', '{loadlib.version_info.major}.{loadlib.version_info.minor}.{loadlib.version_info.micro}.0'),
        StringStruct('InternalName', '{loadlib.SERVER_FILENAME}'),
        StringStruct('LegalCopyright', '\xc2{loadlib.__copyright__}'),
        StringStruct('OriginalFilename', '{loadlib.SERVER_FILENAME}'),
        StringStruct('ProductName', 'Python'),
        StringStruct('ProductVersion', '{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}.0')])
      ]), 
    VarFileInfo([VarStruct('Translation', [0, 1200])])
  ]
)
"""
    filename = 'file_version_info.txt'
    with open(os.path.join(root_path, filename), mode='wt') as fp:
        fp.write(text)
    return filename


def _cli():
    import argparse

    parser = argparse.ArgumentParser(
        description='Create a frozen 32-bit server.',
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        '-s', '--spec',
        help='the path to a PyInstaller .spec file'
    )
    parser.add_argument(
        '-d', '--dest',
        help='the destination directory to save the 32-bit server to\n'
             '(Default is the current directory)'
    )
    parser.add_argument(
        '-p', '--packages',
        nargs='*',
        help='the names of packages to bundle with the 32-bit server\n'
             'Examples:\n'
             '  --packages mypackage\n'
             '  --packages mypackage numpy'
    )
    parser.add_argument(
        '-D', '--data',
        nargs='*',
        help='additional data files to bundle with the 32-bit server\n'
             '(The format is "source:dest_dir", where source is the\n'
             'path to a file (or a directory of files) to add and dest_dir\n'
             'is an optional destination directory, relative to the\n'
             'top-level directory of the frozen 32-bit server, to add\n'
             'the file(s) to. If dest_dir is not specified, the file(s)\n'
             'will be added to the top-level directory of the 32-bit server)\n'
             'Examples:\n'
             '  --data mydata\n'
             '  --data mydata/lib1.dll mydata/bin/lib2.dll:bin\n'
             '  --data mypackage/lib32.dll:mypackage'
    )

    args = parser.parse_args(sys.argv[1:])

    sys.exit(
        main(
            spec=args.spec,
            dest=args.dest,
            packages=args.packages,
            data=args.data,
        )
    )
