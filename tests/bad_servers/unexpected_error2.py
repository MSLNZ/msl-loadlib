from msl.loadlib import Server32


class UnexpectedError(Server32):

    def __init__(self, host, port, **kwargs):
        # any error would be fine
        x = 1 + 'hello'
