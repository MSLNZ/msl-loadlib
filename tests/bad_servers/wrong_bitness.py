import os

from msl.loadlib import Server32


class WrongBitness(Server32):

    def __init__(self, host, port, **kwargs):
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'msl', 'examples', 'loadlib', 'cpp_lib64')
        super(WrongBitness, self).__init__(os.path.abspath(path), 'cdll', host, port, **kwargs)
