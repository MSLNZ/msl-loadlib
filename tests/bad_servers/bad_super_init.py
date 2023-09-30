from msl.loadlib import Server32


class BadSuperInit(Server32):

    def __init__(self, host, port, **kwargs):
        super().__init__()
