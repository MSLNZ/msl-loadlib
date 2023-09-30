from msl.loadlib import Server32


class BadInitArgs2(Server32):

    def __init__(self, host, port, extra, **kwargs):
        pass
