from msl.loadlib import Server32


class BadLibType(Server32):

    def __init__(self, host, port, **kwargs):
        super(BadLibType, self).__init__('doesnotmatter', 'invalid', host, port, **kwargs)
