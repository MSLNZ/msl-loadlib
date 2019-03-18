import os

from msl.loadlib import Server32


class WringBitness(Server32):

    def __init__(self, host, port, quiet, **kwargs):
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'msl', 'examples', 'loadlib', 'cpp_lib64')
        super(WringBitness, self).__init__(os.path.abspath(path), 'cdll', host, port, quiet, **kwargs)
