"""
This module is built in to a 32-bit executable by running :mod:`.freeze_server32`.

The executable is used to host a 32-bit library, :class:`~.server32.Server32`,
so that a module running in a 64-bit Python interpreter, :class:`~.client64.Client64`,
can communicate with the library. This client-server exchange of information is a
form of `inter-process communication <ipc_>`_.

.. _ipc: https://en.wikipedia.org/wiki/Inter-process_communication
"""
from __future__ import print_function

import os
import sys
import code
import inspect
import argparse
import importlib

from msl.loadlib import Server32


def main():
    """Starts a 32-bit server (which is a subclass of :class:`~.server32.Server32`).

    Parses the command-line arguments to run a Python module on a 32-bit server
    to host a 32-bit library. To see the list of command-line arguments that are 
    allowed, run the executable with the ``--help`` flag (or click here_ to view
    the source code of the :obj:`argparse.ArgumentParser` implementation).

    .. _here: http://msl-loadlib.readthedocs.io/en/latest/_modules/msl/loadlib/start_server32.html#main
    """
    parser = argparse.ArgumentParser(
        description='Starts a 32-bit Python interpreter which allows for inter-process communication'
                    ' via a client-server protocol -- i.e., calling a 32-bit process (server) from a'
                    ' 64-bit process (client).',
    )

    parser.add_argument('-m', '--module', default=None,
                        help='the name of the Python module to run on the 32-bit '
                             'server (the module must contain a class that is a '
                             'subclass of msl.loadlib.Server32)')

    parser.add_argument('-asp', '--append-sys-path', default=None,
                        help=r'append path(s) to the sys.path variable on the 32-bit '
                             r'server, e.g., -asp D:\path\to\my_scripts, or for '
                             r'multiple paths separate each path by a semi-colon, '
                             r'e.g., -asp D:\path\to\my_scripts;D:\lib')

    parser.add_argument('-aep', '--append-environ-path', default=None,
                        help=r"append path(s) to the os.environ['PATH'] variable on "
                             r"the 32-bit server, e.g., -aep D:\code\bin, or for "
                             r"multiple paths separate each path by a semi-colon, "
                             r"e.g., -aep D:\code\bin;D:\lib")

    parser.add_argument('-H', '--host', default='127.0.0.1',
                        help='the IP address of the host [default: 127.0.0.1]')

    parser.add_argument('-p', '--port', default=8080,
                        help='the port to open on the host [default: 8080]')

    parser.add_argument('-q', '--quiet', action='store_true',
                        help='whether to hide sys.stdout messages from the server '
                             '[default: False]')

    parser.add_argument('-v', '--version', action='store_true',
                        help='show the Python version that the server is running on '
                             'and exit')

    parser.add_argument('-i', '--interactive', action='store_true',
                        help='start a 32-bit interactive Python console and exit')

    parser.add_argument('-k', '--kwargs', default=None,
                        help='keyword arguments that are passed to the constructor '
                             'of the msl.loadlib.Server32 subclass as "key=value;" '
                             'pairs, e.g., -k a=-2;b=3.14;c=whatever;d=[1,2,3]')

    args = parser.parse_args()

    if args.version:
        print('Python ' + sys.version)
        sys.exit(0)

    # include directories in sys.path
    sys.path.append(os.path.abspath('.'))
    if args.module is not None and os.path.dirname(args.module):
        sys.path.append(os.path.dirname(args.module))
    if args.append_sys_path is not None:
        for path in args.append_sys_path.split(';'):
            if len(path) > 0:
                sys.path.append(os.path.abspath(path))

    # include directories in os.environ['PATH']
    if args.append_environ_path is not None:
        for path in args.append_environ_path.split(';'):
            if len(path) > 0:
                os.environ['PATH'] += os.pathsep + os.path.abspath(path)

    if args.interactive:
        globals().update({'exit': sys.exit, 'quit': sys.exit})
        console = code.InteractiveConsole(locals=dict(globals(), **locals()))
        banner = 'Python ' + sys.version
        banner += '\nType exit() or quit() or <CTRL+Z then Enter> to terminate the console.'
        console.interact(banner=banner)
        sys.exit(0)

    # build the keyword-argument dictionary
    kwargs = {}
    if args.kwargs is not None:
        for item in args.kwargs.split(';'):
            item_split = item.split('=')
            if len(item_split) == 1:
                key = item_split[0].strip()
                value = ''
            else:
                key = item_split[0].strip()
                value = item_split[1].strip()
            if len(key) > 0:
                kwargs[key] = value

    # if you get to this point in the script that means you want to start a server for
    # inter-process communication and therefore args.module must have a value
    if args.module is None:
        print('You must specify a Python module to run on the 32-bit server (i.e., -m my_module)')
        print('Cannot start 32-bit server.\n')
        sys.exit(0)

    args.module = os.path.basename(args.module)
    if args.module.endswith('.py'):
        args.module = args.module[:-3]

    if args.module.startswith('.'):
        print('ImportError: ' + args.module)
        print('Cannot perform relative imports.')
        print('Cannot start 32-bit server.\n')
        sys.exit(0)

    try:
        mod = importlib.import_module(args.module)
    except ImportError as e:
        print('ImportError: {}'.format(e))
        print('The missing module must be in sys.path (see the --append-sys-path argument)')
        print('The paths in sys.path are:')
        for path in sys.path[2:]:  # the first two paths are TEMP folders from the frozen application
            print('\t' + path)
        print('Cannot start 32-bit server.\n')
        sys.exit(0)

    # ensure that there is a subclass of Server32 in the module
    server32 = None
    for name in dir(mod):
        attr = getattr(mod, name)
        if inspect.isclass(attr) and (name != 'Server32') and issubclass(attr, Server32):
            server32 = attr
            break

    if server32 is None:
        print('AttributeError: module {}.py'.format(args.module))
        print('Module does not contain a class that is a subclass of Server32')
        print('Cannot start 32-bit server.\n')
        sys.exit(0)

    try:
        app = server32(args.host, args.port, args.quiet, **kwargs)
    except TypeError as e:
        print('TypeError: {}'.format(e))
        print('The Server32 subclass must be initialized using\n')
        print('class {}(Server32):'.format(server32.__name__))
        print('    def __init__(self, host, port, quiet, **kwargs):\n')
        print('Cannot start 32-bit server.\n')
        sys.exit(0)

    if not args.quiet:
        print('Python ' + sys.version)
        print('Serving {} on http://{}:{}'.format(os.path.basename(app.path), args.host, args.port))

    try:
        app.serve_forever()
    except KeyboardInterrupt:
        if not args.quiet:
            print('KeyboardInterrupt', end=' -- ')
    finally:
        if not args.quiet:
            print('Stopped http://{}:{}'.format(args.host, args.port))


if __name__ == '__main__':
    main()
