"""
Creates a 32-bit server to use for
`inter-process communication <https://en.wikipedia.org/wiki/Inter-process_communication>`_.

This module must be run from a 32-bit Python interpreter with PyInstaller_ installed.

If you want to re-freeze the 32-bit server, for example, if you want a 32-bit version of
:mod:`numpy` to be available on the server, then run the following with a 32-bit Python
interpreter that has the packages that you want to be available on the server installed

.. code-block:: pycon

   >>> from msl.loadlib import freeze_server32
   >>> freeze_server32.main()  # doctest: +SKIP

.. _PyInstaller: https://www.pyinstaller.org/
.. _Python for .NET: https://pypi.python.org/pypi/pythonnet/
.. _comtypes: https://pythonhosted.org/comtypes/#
"""
import os
import sys
import shutil
import subprocess
try:
    from urllib import urlopen  # Python 2
except ImportError:
    from urllib.request import urlopen

try:
    from msl import loadlib
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from msl import loadlib


def main(spec=None, requires_pythonnet=True, requires_comtypes=True):
    """Creates a 32-bit Python server.

    Uses PyInstaller_ to create a frozen 32-bit Python executable. This executable
    starts a 32-bit server, :class:`~.server32.Server32`, which hosts a Python
    module that can load a 32-bit library.

    .. versionchanged:: 0.5
       Added the `requires_pythonnet` and `requires_comtypes` arguments.

    Parameters
    ----------
    spec : :class:`str`, optional
        If you want to freeze using a PyInstaller_ .spec file then you can specify the 
        path to the .spec file.
    requires_pythonnet : :class:`bool`, optional
        Whether `Python for .NET`_ must be available on the 32-bit server.
    requires_comtypes : :class:`bool`, optional
        Whether comtypes_ must be available on the 32-bit server. If you using a
        non-Windows operating system then this argument is ignored.
    """
    if loadlib.IS_PYTHON_64BIT:
        print('Must run {} using a 32-bit Python interpreter'.format(os.path.basename(__file__)))
        return

    missing_packages = []
    try:
        import PyInstaller
    except ImportError:
        missing_packages.append('pyinstaller')

    if requires_pythonnet:
        try:
            import clr
        except ImportError:
            missing_packages.append('pythonnet')

    if loadlib.IS_WINDOWS and requires_comtypes:
        try:
            import comtypes
        except ImportError:
            missing_packages.append('comtypes')
        except OSError:
            # OSError: [WinError -2147417850] Cannot change thread mode after it is set
            # don't care about this error since comtypes is indeed installed
            pass

    if missing_packages:
        print('Packages are missing to be able to create the 32-bit server, run:')
        print('pip install ' + ' '.join(missing_packages))
        return

    # start the freezing process

    here = os.path.abspath(os.path.dirname(__file__))
    cmd = [
        'pyinstaller',
        '--distpath', here,
        '--noconfirm',
    ]

    if spec is None:
        spec_file = '{}.spec'.format(loadlib.SERVER_FILENAME)
        if os.path.exists(spec_file):
            yn = input('A {0} file exists. You may want to run "python freeze_server32.py {0}"\n'
                       'Do you want to continue and overwrite the spec file (y/[n]):'.format(spec_file))
            if yn.lower() not in ('y', 'yes'):
                print('Aborted.')
                return
        cmd.extend([
            '--name', loadlib.SERVER_FILENAME,
            '--onefile',
            '--clean',
            '--hidden-import', 'msl.examples.loadlib',
        ])
        if requires_pythonnet:
            cmd.extend(['--hidden-import', 'clr'])
        if loadlib.IS_WINDOWS and requires_comtypes:
            cmd.extend(['--hidden-import', 'comtypes'])
        cmd.extend(_get_standard_modules())
        cmd.append(os.path.join(here, 'start_server32.py'))
    else:
        cmd.append(spec)
    subprocess.call(cmd)

    # the --version-file option for pyinstaller does not currently work on Windows, this is a fix
    verpatch = os.path.join(here, 'verpatch.exe')
    if loadlib.IS_WINDOWS and os.path.isfile(verpatch):
        ver = [verpatch,
               os.path.join(here, loadlib.SERVER_FILENAME),
               '/va', '{0}.{1}.{2}'.format(*loadlib.version_info) + '.0',
               '/pv', '{0}.{1}.{2}.{4}'.format(*sys.version_info),
               '/s', 'description', 'Access a 32-bit library from 64-bit Python',
               '/s', 'product', 'Python 32-bit server',
               '/s', 'copyright', loadlib.__copyright__]
        subprocess.call(ver)

    # cleanup
    shutil.rmtree('./build/' + loadlib.SERVER_FILENAME)
    if not os.listdir('./build'):
        shutil.rmtree('./build')
    if loadlib.IS_WINDOWS:
        # pyinstaller is able to include Python.Runtime.dll and Python.Runtime.dll.config
        # automatically in the build, so we don't need to keep the .spec file
        os.remove(loadlib.SERVER_FILENAME + '.spec')

    # create the .NET Framework config file
    loadlib.utils.check_dot_net_config(os.path.join(here, loadlib.SERVER_FILENAME))


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

    Returns
    -------
    :class:`list` of :class:`str`
        A list of modules to be included and excluded.
    """

    # the frozen application is never meant to create GUIs or to add
    # support for building and installing Python modules
    ignore_list = ['__main__', 'distutils', 'ensurepip', 'tkinter', 'turtle']

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
    url = 'https://docs.python.org/{0}.{1}/py-modindex.html'.format(*sys.version_info)
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
