"""
Used for testing the CLI argparse.
"""
import os
from msl.loadlib import Client64


class ClientArgParse(Client64):

    def __init__(self, append_sys_path, append_environ_path, **kwargs):
        Client64.__init__(
            self,
            'cli32',
            append_sys_path=[os.path.dirname(__file__)]+append_sys_path,
            append_environ_path=append_environ_path,
            **kwargs
        )

    def is_in_sys_path(self, path):
        return self.request32('is_in_sys_path', path)

    def is_in_environ_path(self, path):
        return self.request32('is_in_environ_path', path)

    def get_kwarg(self, key):
        return self.request32('get_kwarg', key)
