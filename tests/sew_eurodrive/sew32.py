import os

from msl.loadlib import Server32


class SEWEuroDrive32(Server32):

    def __init__(self, host, port, **kwargs):
        path = os.path.join(os.path.dirname(__file__), 'FirstDll.dll')
        super(SEWEuroDrive32, self).__init__(path, 'clr', host, port)
        self.first_class = self.lib.FirstDll.FirstClass()

    def do_something(self, value):
        # returns "value/3/2"
        return self.first_class.DoSometing(value)
