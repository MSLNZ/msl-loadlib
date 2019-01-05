from msl.loadlib import Server32


class BadSuperArgs(Server32):

    def __init__(self, host, port, quiet, **kwargs):
        super(BadSuperArgs, self).__init__()
