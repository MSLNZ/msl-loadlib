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

from msl.loadlib import (
    Server32,
    SERVER_FILENAME,
)


def main():
    """Starts a 32-bit server (which is a subclass of :class:`~.server32.Server32`).

    Parses the command-line arguments to run a Python module on a 32-bit server
    to host a 32-bit library. To see the list of command-line arguments that are
    allowed, run the executable with the ``--help`` flag (or click here_ to view
    the source code of the :class:`argparse.ArgumentParser` implementation).

    .. _here: https://msl-loadlib.readthedocs.io/en/latest/_modules/msl/loadlib/start_server32.html#main
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

    parser.add_argument('-s', '--append-sys-path', default=None,
                        help=r'append path(s) to the sys.path variable on the 32-bit '
                             r'server, e.g., -s D:\path\to\my_scripts, or for '
                             r'multiple paths separate each path by a semi-colon, '
                             r'e.g., -s D:\path\to\my_scripts;D:\lib')

    parser.add_argument('-e', '--append-environ-path', default=None,
                        help=r"append path(s) to the os.environ['PATH'] variable on "
                             r"the 32-bit server, e.g., -e D:\code\bin, or for "
                             r"multiple paths separate each path by a semi-colon, "
                             r"e.g., -e D:\code\bin;D:\lib")

    parser.add_argument('-H', '--host', default='127.0.0.1',
                        help='the IP address of the host [default: 127.0.0.1]')

    parser.add_argument('-p', '--port', default=8080,
                        help='the port to open on the host [default: 8080]')

    parser.add_argument('-v', '--version', action='store_true',
                        help='show the Python version that the server is running on '
                             'and exit')

    parser.add_argument('-i', '--interactive', action='store_true',
                        help='start a 32-bit interactive Python console and exit')

    parser.add_argument('-k', '--kwargs', default=None,
                        help='keyword arguments that are passed to the constructor '
                             'of the msl.loadlib.Server32 subclass as "key=value;" '
                             'pairs, e.g., -k a=-2;b=3.14;c=whatever;d=[1,2,3]')

    parser.add_argument('-q', '--quiet', action='store_true',
                        help='ignored and will be removed in a future release')

    args = parser.parse_args()

    if args.version:
        print('Python ' + sys.version)
        return 0

    # include directories in sys.path
    sys.path.append(os.path.abspath('.'))
    if args.module is not None and os.path.dirname(args.module):
        sys.path.append(os.path.dirname(args.module))
    if args.append_sys_path is not None:
        for path in args.append_sys_path.split(';'):
            if path:
                sys.path.append(os.path.abspath(path))

    # include directories in os.environ['PATH']
    if args.append_environ_path is not None:
        for path in args.append_environ_path.split(';'):
            if path:
                os.environ['PATH'] += os.pathsep + os.path.abspath(path)

    if args.interactive:
        globals().update({'exit': sys.exit, 'quit': sys.exit})
        console = code.InteractiveConsole(locals=dict(globals(), **locals()))
        banner = 'Python ' + sys.version
        banner += '\nType exit() or quit() or <CTRL+Z then Enter> to terminate the console.'
        console.interact(banner=banner)
        return 0

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

    if args.quiet:
        print('DeprecationWarning: the --quiet flag is ignored and will be removed in a future release')

    # if you get to this point in the script that means you want to start a server for
    # inter-process communication and therefore args.module must have a value
    if not args.module:
        err = 'You must specify a Python module to run on the 32-bit server.\n' \
              'For example: {} -m my_module.py\n' \
              'Cannot start the 32-bit server.'.format(SERVER_FILENAME)
        print(err, file=sys.stderr)
        return -1

    args.module = os.path.basename(args.module)
    if args.module.endswith('.py'):
        args.module = args.module[:-3]

    if args.module.startswith('.'):
        err = 'ImportError: {}\n' \
              'Cannot perform relative imports.\n' \
              'Cannot start the 32-bit server.'.format(args.module)
        print(err, file=sys.stderr)
        return -1

    try:
        mod = importlib.import_module(args.module)
    except ImportError as e:
        # the first two paths are TEMP folders from the frozen application
        paths = '\n  '.join(item for item in sys.path[2:])
        err = 'ImportError: {}\n' \
              'The missing module must be in sys.path (see the --append-sys-path option)\n' \
              'The paths in sys.path are:\n  {}\n' \
              'Cannot start the 32-bit server.'.format(e, paths)
        print(err, file=sys.stderr)
        return -1

    # ensure that there is a subclass of Server32 in the module
    cls = None
    for name, obj in inspect.getmembers(mod, inspect.isclass):
        if name != 'Server32' and issubclass(obj, Server32):
            cls = obj
            break

    if cls is None:
        err = 'AttributeError: module {}.py\n' \
              'Module does not contain a class that is a subclass of Server32.\n' \
              'Cannot start the 32-bit server.'.format(args.module)
        print(err, file=sys.stderr)
        return -1

    server, err = None, ''
    try:
        server = cls(args.host, args.port, **kwargs)
    except Exception as e:
        err = '{}: {}\n'.format(e.__class__.__name__, e)
        if e.__class__.__name__ == 'TypeError' and '__init__' in err:
            # support the old syntax where the Server32 required a 'quiet' argument
            if "missing 1 required positional argument: 'quiet'" in err:
                try:
                    server = cls(args.host, args.port, True, **kwargs)
                except Exception as e:
                    err = '{}: {}\n'.format(e.__class__.__name__, e)

    if server is None:
        err += 'The \'{0}\' class must be defined with the following syntax:\n\n' \
               'class {0}(Server32):\n' \
               '    def __init__(self, host, port, **kwargs):\n' \
               '        super({0}, self).__init__(path, libtype, host, port, **kwargs)\n\n' \
               'Cannot start the 32-bit server.'.format(cls.__name__)
        print(err, file=sys.stderr)
        return -1

    if not hasattr(server, '_library'):
        err = 'The super() method was never called.\n' \
              'The \'{0}\' class must be defined with the following syntax:\n\n' \
              'class {0}(Server32):\n' \
              '    def __init__(self, host, port, **kwargs):\n' \
              '        super({0}, self).__init__(path, libtype, host, port, **kwargs)\n\n' \
              'Cannot start the 32-bit server.'.format(cls.__name__)
        print(err, file=sys.stderr)
        return -1

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        # only get here if there is an exception in the serve_forever() code.
        # error handling for a request is handled by the RequestHandler class
        print('{}: {}'.format(e.__class__.__name__, e), file=sys.stderr)
    finally:
        server.server_close()
        return 0


if __name__ == '__main__':
    sys.exit(main())
