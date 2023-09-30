from msl.loadlib import Server32


class BadLibType(Server32):

    def __init__(self, host, port, **kwargs):
        super().__init__('doesnotmatter', 'invalid', host, port, **kwargs)
