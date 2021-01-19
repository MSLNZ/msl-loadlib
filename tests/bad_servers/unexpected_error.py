import os

from msl.loadlib import Server32


class UnexpectedError(Server32):

    def __init__(self, host, port, **kwargs):
        # any error would be fine
        x = 1/0

        path = os.path.join(os.path.dirname(__file__), '..', '..', 'msl', 'examples', 'loadlib', 'cpp_lib32')
        super(UnexpectedError, self).__init__(os.path.abspath(path), 'cdll', host, port, **kwargs)
