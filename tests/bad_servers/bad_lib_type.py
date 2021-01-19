import os

from msl.loadlib import Server32


class BadLibType(Server32):

    def __init__(self, host, port, **kwargs):
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'msl', 'examples', 'loadlib', 'cpp_lib32')
        super(BadLibType, self).__init__(os.path.abspath(path), 'invalid', host, port, **kwargs)
