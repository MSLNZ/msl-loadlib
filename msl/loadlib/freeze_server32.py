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
import glob
import shutil
import subprocess

SERVER_FILENAME = 'server32-{}'.format(sys.platform)


def main():
    """
    Creates a `frozen <http://www.pyinstaller.org/>`_ 32-bit Python server.

    Uses `PyInstaller <http://www.pyinstaller.org/>`_ to create a `frozen
    <http://www.pyinstaller.org/>`_ 32-bit Python executable. This executable starts
    a server, :class:`~.server32.Server32`, which hosts a Python module that can load
    a 32-bit library.
    """

    # this script must be run from its own directory so that the output files are in this folder.
    old_dir = None
    if not os.getcwd() == os.path.dirname(os.path.abspath(__file__)):
        old_dir = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # make sure that the msl package is visible before importing it
    sys.path.insert(0, os.path.join('..', '..'))
    from msl import loadlib

    if loadlib.IS_PYTHON2:
        from urllib import urlopen
    elif loadlib.IS_PYTHON3:
        from urllib.request import urlopen
    else:
        raise NotImplementedError('Python major version is not 2 or 3')

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

    _freeze(urlopen, loadlib)

    # set the working directory back to the previous one
    if old_dir is not None:
        os.chdir(old_dir)


def _freeze(urlopen, loadlib):
    """
    Calls PyInstaller to perform the freezing process.
    """
    cmd = ['pyinstaller',
           '--name', SERVER_FILENAME,
           '--distpath', '.',
           '--onefile',
           '--noconfirm',
           '--clean',
           '--hidden-import', 'clr',
           ]
    cmd.extend(_get_standard_modules(urlopen))
    cmd.append('./start_server32.py')
    subprocess.call(cmd)

    # the --version-file option for pyinstaller does not currently work on Windows, this is a fix
    if loadlib.IS_WINDOWS:
        ver = ['verpatch', SERVER_FILENAME + '.exe',
               '/va', loadlib.__version__ + '.0',
               '/pv', '{0}.{1}.{2}.{4}'.format(*sys.version_info),
               '/s', 'description', 'Access a 32-bit library from 64-bit Python',
               '/s', 'product', 'Python 32-bit server',
               '/s', 'copyright', loadlib.__copyright__]
        subprocess.call(ver)

    # cleanup
    os.remove(SERVER_FILENAME + '.spec')
    shutil.rmtree('./build')

    # create the .NET Framework config file
    for name in glob.glob('./{}*'.format(SERVER_FILENAME)):
        if not name.endswith('.config'):
            loadlib.LoadLibrary.check_dot_net_config(name)


def _get_standard_modules(urlopen):
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
    main()
