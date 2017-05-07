"""
This module is built into a 32-bit executable by running :mod:`.freeze_server32`.

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
    to host a 32-bit library. To see the list of arguments that are allowed,
    run the executable with the ``--help`` flag.
    """
    parser = argparse.ArgumentParser(
        description='Starts a 32-bit Python interpreter which allows for inter-process communication'
                    ' via a client-server protocol -- i.e., calling a 32-bit process (server) from a'
                    ' 64-bit process (client).')

    parser.add_argument('-m', '--module', default=None,
                        help='the Python module to run on the 32-bit server (the module must contain'
                             ' a class that is a subclass of msl.loadlib.Server32)')

    parser.add_argument('-a', '--append-path', default=None,
                        help='append path(s) to sys.path, e.g., D:\code\scripts or for multiple '
                             'paths [D:\code\scripts,D:\code\libs]')

    parser.add_argument('-H', '--host', default='127.0.0.1',
                        help='the IP address of the host [default: 127.0.0.1]')

    parser.add_argument('-p', '--port', default=8080,
                        help='the port to open on the host [default: 8080]')

    parser.add_argument('-q', '--quiet', action='store_true',
                        help='whether to hide sys.stdout messages from the server [default: False]')

    parser.add_argument('-v', '--version', action='store_true',
                        help='show the Python version that the server is running on and exit')

    parser.add_argument('-i', '--interactive', action='store_true',
                        help='start a 32-bit interactive Python console and exit')

    args = parser.parse_args()

    if args.version:
        print('Python ' + sys.version)
        sys.exit(0)

    # include folders in sys.path
    sys.path.append(os.path.abspath('.'))
    if args.module is not None and os.path.dirname(args.module):
        sys.path.append(os.path.dirname(args.module))
    if args.append_path is not None:
        if args.append_path.startswith('[') and args.append_path.endswith(']'):
            for path in args.append_path[1:-1].split(','):
                sys.path.append(os.path.abspath(path))
        else:
            sys.path.append(os.path.abspath(args.append_path))

    if args.interactive:
        globals().update({'exit': sys.exit, 'quit': sys.exit})
        console = code.InteractiveConsole(locals=dict(globals(), **locals()))
        banner = 'Python ' + sys.version
        banner += '\nType exit() or quit() or <CTRL+Z then Enter> to terminate the interactive console'
        console.interact(banner=banner)
        sys.exit(0)

    # if you get to this point in the script that means you want to start a server for
    # inter-process communication and therefore args.module must have a value
    if args.module is None:
        print('You must pass in a Python module to run on the 32-bit server (i.e., -m my_module)')
        sys.exit(0)

    args.module = os.path.basename(args.module)
    if len(args.module) > 3 and args.module[-3:] == '.py':
        args.module = args.module[:-3]

    if args.module.startswith('.'):
        print('ImportError: ' + args.module)
        print('Cannot perform relative imports')
        sys.exit(0)

    try:
        mod = importlib.import_module(args.module)
    except ImportError as e:
        print('ImportError: {}'.format(e))
        print('The missing module must be in sys.path (see the --append-path argument)')
        print('The paths in sys.path are:')
        for path in sys.path[2:]:  # the first two paths are TEMP folders from the frozen application
            print('\t' + path)
        print('Cannot start server.')
        print()
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
        print('Cannot start server.')
        print()
        sys.exit(0)

    app = server32(args.host, args.port, args.quiet)

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
