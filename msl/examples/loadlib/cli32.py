"""
Used for testing the CLI argparse.
"""
import os
import sys
from msl.loadlib import Server32


class ServerArgParse(Server32):

    def __init__(self, host, port, quiet, **kwargs):
        # load any dll since it won't be called
        Server32.__init__(self, 'cpp_lib32', 'cdll', host, port, quiet)
        self.kwargs = kwargs

    def is_in_sys_path(self, path):
        return os.path.abspath(path) in sys.path

    def is_in_environ_path(self, path):
        return os.path.abspath(path) in os.environ['PATH']

    def get_kwarg(self, key):
        return self.kwargs[key]
