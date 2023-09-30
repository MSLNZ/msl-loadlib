import os

from msl.loadlib import Server32


class WrongBitness(Server32):

    def __init__(self, host, port, **kwargs):
        path = os.path.join(Server32.examples_dir(), 'cpp_lib64')
        super().__init__(path, 'cdll', host, port, **kwargs)
