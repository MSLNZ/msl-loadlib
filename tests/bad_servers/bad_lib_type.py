from msl.loadlib import Server32


class BadLibType(Server32):

    def __init__(self, host, port, **kwargs):
        super().__init__('does_not_matter', 'invalid', host, port, **kwargs)
