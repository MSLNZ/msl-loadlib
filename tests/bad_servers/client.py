from msl.loadlib import Client64


class Client(Client64):
    def __init__(self, module32):
        super().__init__(module32, timeout=5)
