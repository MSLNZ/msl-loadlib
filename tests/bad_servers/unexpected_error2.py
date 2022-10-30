from msl.loadlib import Server32


class UnexpectedError(Server32):

    def __init__(self, host, port, quiet, **kwargs):
        # include the 'quiet' positional argument

        # any error would be fine
        x = 1 + 'hello'
