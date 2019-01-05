from msl.loadlib import Server32


class BadLibPath(Server32):

    def __init__(self, host, port, quiet, **kwargs):
        super(BadLibPath, self).__init__('doesnotexist', 'cdll', host, port, quiet, **kwargs)
