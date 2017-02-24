"""
Creates a `frozen <http://www.pyinstaller.org/>`_ 32-bit server to use for
`inter-process communication <https://en.wikipedia.org/wiki/Inter-process_communication>`_.

This module creates a 32-bit executable. The executable starts a 32-bit server to
host a 32-bit library. A client module running within a 64-bit Python interpreter
can communicate with the 32-bit library by sending requests to the server. The server
calls the library to execute the request and then the server sends a response back
to the client.

This module must be run from a 32-bit Python interpreter with both
`PyInstaller <http://www.pyinstaller.org/>`_ (to create the executable) and
`Python .NET <https://pypi.python.org/pypi/pythonnet/>`_ (to be able to load a .NET
Framework library) installed.
"""
import os
import sys
import shutil
import subprocess

try:
    from msl import loadlib
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from msl import loadlib

if loadlib.IS_PYTHON2:
    from urllib import urlopen
elif loadlib.IS_PYTHON3:
    from urllib.request import urlopen
else:
    raise NotImplementedError('Python major version is not 2 or 3')


def main(spec=None):
    """
    Creates a `frozen <PyInstaller_>`_ 32-bit Python server.

    Uses PyInstaller_ to create a `frozen <PyInstaller_>`_ 32-bit Python executable.
    This executable starts a server, :class:`~.server32.Server32`, which hosts a Python
    module that can load a 32-bit library.

    Args:
        spec (str, optional): If you want to freeze using a PyInstaller_ .spec file then you
            can specify the path to the .spec file. Default is :py:data:`None`.

    .. _PyInstaller: http://www.pyinstaller.org/
    """
    if loadlib.IS_PYTHON_64BIT:
        print('Must run {} using a 32-bit Python interpreter'.format(os.path.basename(__file__)))
        sys.exit(0)

    try:
        import PyInstaller
    except ImportError:
        print('PyInstaller not found, run:')
        print('$ pip install pyinstaller')
        sys.exit(0)

    try:
        import clr
    except ImportError:
        print('pythonnet not found, run:')
        print('$ pip install pythonnet')
        sys.exit(0)

    # start the freezing process

    here = os.path.abspath(os.path.dirname(__file__))
    cmd = ['pyinstaller',
           '--distpath', here,
           '--noconfirm',
           ]
    if spec is None:
        cmd.extend(['--name', loadlib.SERVER_FILENAME,
                    '--onefile',
                    '--clean',
                    '--hidden-import', 'clr',
                    ])
        cmd.extend(_get_standard_modules())
        cmd.append(os.path.join(here, 'start_server32.py'))
    else:
        cmd.append(spec)
    subprocess.call(cmd)

    # the --version-file option for pyinstaller does not currently work on Windows, this is a fix
    if loadlib.IS_WINDOWS:
        ver = [os.path.join(here, 'verpatch'),
               os.path.join(here, loadlib.SERVER_FILENAME),
               '/va', loadlib.__version__ + '.0',
               '/pv', '{0}.{1}.{2}.{4}'.format(*sys.version_info),
               '/s', 'description', 'Access a 32-bit library from 64-bit Python',
               '/s', 'product', 'Python 32-bit server',
               '/s', 'copyright', loadlib.__copyright__]
        subprocess.call(ver)

    # cleanup
    shutil.rmtree('./build')
    if loadlib.IS_WINDOWS:
        # pyinstaller is able to include Python.Runtime.dll and Python.Runtime.dll.config
        # automatically in the build, so we don't need to keep the .spec file
        os.remove(loadlib.SERVER_FILENAME + '.spec')

    # create the .NET Framework config file
    loadlib.LoadLibrary.check_dot_net_config(os.path.join(here, loadlib.SERVER_FILENAME))


def _get_standard_modules():
    """
    Returns a list of standard python modules to include and exclude in the
    frozen application.

    PyInstaller does not automatically bundle all of the standard Python modules
    into the frozen application. This
    method parses the 'docs.python.org' website for the list of standard Python
    modules that are available.

    The 'pyinstaller --exclude-module' option ensures that the module is
    excluded from the frozen application.

    The 'pyinstaller --hidden-import' option ensures that the module is included
    into the frozen application (only if the module is available for the operating
    system that is running this script).

    Returns:
       list[str]: A list of modules to be included and excluded
    """

    # the frozen application is never meant to create GUIs or to add
    # support for building and installing Python modules
    ignore_list = ['__main__', 'distutils', 'ensurepip', 'tkinter', 'turtle']

    url = 'https://docs.python.org/{0}.{1}/py-modindex.html'.format(*sys.version_info)
    source = urlopen(url).read().decode().split('#module-')
    modules = [source[idx].split('"><code')[0] for idx in range(1, len(source))]

    included_modules, excluded_modules = [], []
    for module in modules:
        include_module = True
        for mod in ignore_list:
            if mod in module:
                excluded_modules.extend(['--exclude-module', module])
                include_module = False
                break
        if include_module:
            included_modules.extend(['--hidden-import', module])
    return included_modules + excluded_modules


if __name__ == '__main__':
    spec = None
    if len(sys.argv) > 1:
        if sys.argv[1].endswith('.spec'):
            spec = sys.argv[1]
        else:
            raise IOError('Must pass in a PyInstaller .spec file')
    main(spec)
