"""
This module is built in to a 32-bit executable by running :mod:`.freeze_server32`.

The executable is used to host a 32-bit library, :class:`~.server32.Server32`,
so that a module running in a 64-bit Python interpreter, :class:`~.client64.Client64`,
can communicate with the library. This client-server exchange of information is a
form of `inter-process communication <ipc_>`_.

.. _ipc: https://en.wikipedia.org/wiki/Inter-process_communication
"""
import argparse
import code
import importlib
import inspect
import os
import sys
import tempfile
import traceback

from msl.loadlib import Server32
from msl.loadlib.constants import SERVER_FILENAME


def main():
    """Starts a 32-bit server (which is a subclass of :class:`~.server32.Server32`).

    Parses the command-line arguments to run a Python module on a 32-bit server
    to host a 32-bit library. To see the list of command-line arguments that are
    allowed, run the executable with the ``--help`` flag (or click here_ to view
    the source code of the :class:`argparse.ArgumentParser` implementation).

    .. _here: https://msl-loadlib.readthedocs.io/en/stable/_modules/msl/loadlib/start_server32.html#main
    """
    parser = argparse.ArgumentParser(
        description='Created by the msl-loadlib Python package.\n\n'
                    'Runs a 32-bit Python interpreter for inter-process communication for the client-server\n'
                    'protocol, i.e., call a 32-bit process (server) from a 64-bit process (client).',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-i', '--interactive', action='store_true',
                        help='run an interactive console with the 32-bit server and exit')

    parser.add_argument('-v', '--version', action='store_true',
                        help='show the Python version of the 32-bit server and exit')

    parser.add_argument('-s', '--append-sys-path', default=None,
                        help='append path(s) to sys.path on the 32-bit server\n'
                             '(to append multiple paths, separate each path with a semicolon)')

    parser.add_argument('-e', '--append-environ-path', default=None,
                        help='append path(s) to os.environ["PATH"] on the 32-bit server\n'
                             '(to append multiple paths, separate each path with a semicolon)')

    parser.add_argument('-m', '--module', default=None,
                        help='a Python module to run on the 32-bit server\n'
                             '(the module must contain a subclass of Server32)')

    parser.add_argument('-H', '--host', default='127.0.0.1',
                        help='hostname or IP address to run the server on [default: 127.0.0.1]')

    parser.add_argument('-p', '--port', default=8080,
                        help='the port to open on the host [default: 8080]')

    parser.add_argument('-k', '--kwargs', default=None,
                        help='keyword arguments that are passed to the constructor of the\n'
                             'Server32 subclass as name=value pairs separated with a semicolon\n'
                             'e.g., --kwargs a=100;b=3.14;c=filename.csv')

    args = parser.parse_args()

    if args.version:
        print(f'Python {sys.version}')
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
        import builtins

        class Quitter:
            def __repr__(self):
                ctrl = '"Ctrl-Z then Enter"' if sys.platform == 'win32' else 'Ctrl-D (i.e. EOF)'
                return f'Use exit(), quit() or {ctrl} to exit the 32-bit server console'

            def __call__(self, *args, **kwargs):
                raise SystemExit

        quitter = Quitter()
        builtins.exit = quitter
        builtins.quit = quitter

        locs = dict((k, v) for k, v in globals().items() if k.startswith('_'))
        locs['__doc__'] = 'Interactive console for the 32-bit server (msl-loadlib).'
        console = code.InteractiveConsole(locals=locs)
        try:
            console.interact(banner=f'Python {sys.version} on {sys.platform}\n{quitter}', exitmsg='')
        except SystemExit:
            console.write('\n')
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

    # if you get to this point in the script that means you want to start a server for
    # inter-process communication and therefore args.module must have a value
    if not args.module:
        err = (f'You must specify a Python module to run on the 32-bit server.\n'
               f'For example: {SERVER_FILENAME} -m my_module\n'
               f'Cannot start the 32-bit server.')
        print(err, file=sys.stderr)
        return -1

    args.module = os.path.basename(args.module)
    if args.module.endswith('.py'):
        args.module = args.module[:-3]

    if args.module.startswith('.'):
        err = (f'ImportError: {args.module}\n'
               f'Cannot perform relative imports.\n'
               f'Cannot start the 32-bit server.')
        print(err, file=sys.stderr)
        return -1

    f = os.path.join(tempfile.gettempdir(), f'msl-loadlib-{args.host}-{args.port}.txt')
    with open(f, mode='wt') as fp:
        fp.write(f'{os.getpid()}\n{sys._MEIPASS}')  # noqa: sys._MEIPASS exists

    try:
        mod = importlib.import_module(args.module)
    except ImportError as e:
        # ignore the folders from the unfrozen application
        paths = '\n  '.join(item for item in sys.path
                            if not item.startswith(sys._MEIPASS))  # noqa: sys._MEIPASS exists
        err = (f'ImportError: {e}\n'
               f'The missing module must be in sys.path (see the --append-sys-path option)\n'
               f'The paths in sys.path are:\n  {paths}\n\n'
               f'Cannot start the 32-bit server.')
        print(err, file=sys.stderr)
        return -1
    except:  # noqa: PEP 8: E722 do not use bare 'except'
        err = (f'Importing {args.module!r} on the 32-bit server raised '
               f'the following exception:\n\n{traceback.format_exc()}\n'
               f'Cannot start the 32-bit server.')
        print(err, file=sys.stderr)
        return -1

    # ensure that there is a subclass of Server32 in the module
    cls = None
    for name, obj in inspect.getmembers(mod, inspect.isclass):
        if name != 'Server32' and issubclass(obj, Server32):
            cls = obj
            break

    if cls is None:
        err = (f'AttributeError: module {args.module}.py\n'
               f'Module does not contain a class that is a subclass of Server32.\n'
               f'Cannot start the 32-bit server.')
        print(err, file=sys.stderr)
        return -1

    server, error, tb = None, None, None
    try:
        server = cls(args.host, args.port, **kwargs)
    except Exception as e:
        error = e
        tb = traceback.format_exc()

    if error is not None:
        err = f'Instantiating {cls.__name__!r} raised the following exception:\n\n{tb}\n'
        if error.__class__.__name__ == 'TypeError' and '__init__' in str(error):
            name = cls.__name__
            err += (f'Check that the {name!r} class is defined with the following syntax\n\n'
                    f'class {name}(Server32):\n'
                    f'    def __init__(self, host, port, **kwargs):\n'
                    f'        super().__init__(path, libtype, host, port, **kwargs)\n\n')

        err += 'Cannot start the 32-bit server.'
        print(err, file=sys.stderr)
        return -1

    if not hasattr(server, '_library'):
        name = cls.__name__
        err = (f'The super() function was never called in the Server32 subclass.\n'
               f'Check that the {name!r} class is defined with the following syntax\n\n'
               f'class {name}(Server32):\n'
               f'    def __init__(self, host, port, **kwargs):\n'
               f'        super().__init__(path, libtype, host, port, **kwargs)\n\n'
               f'Cannot start the 32-bit server.')
        print(err, file=sys.stderr)
        return -1

    try:
        server.server_bind()
        server.server_activate()
        server.serve_forever()
    except (SystemExit, KeyboardInterrupt):
        pass
    except:  # noqa: PEP 8: E722 do not use bare 'except'
        # Can only get here if starting the HTTPServer raised an exception.
        # Error handling for a request is handled by the RequestHandler class.
        print(f'Binding, activating and starting the HTTPServer raised the '
              f'following exception\n{traceback.format_exc()}', file=sys.stderr)
        return -1
    finally:
        server.server_close()


if __name__ == '__main__':
    sys.exit(main())
