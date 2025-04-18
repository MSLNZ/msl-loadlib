from msl.loadlib import LoadLibrary
from msl.loadlib import Server32

# comtypes on the 32-bit server will try to import numpy
# remove site-packages before importing msl.loadlib.activex
if Server32.is_interpreter():
    Server32.remove_site_packages_64bit()

from msl.loadlib.activex import Application

prog_id = "MediaPlayer.MediaPlayer.1"


class ActiveX(Server32):
    def __init__(self, host, port):
        super().__init__(prog_id, "activex", host, port)
        self._app = Application()

    def this(self):
        return self.lib.IsSoundCardEnabled()

    def reload(self):
        return self._app.load(prog_id).IsSoundCardEnabled()

    @staticmethod
    def load_library():
        return LoadLibrary(prog_id, "activex").lib.IsSoundCardEnabled()

    def error1(self):
        try:
            self._app.load("ABC.DEF.GHI")
        except OSError as e:
            return str(e)
        else:
            msg = "Did not raise OSError"
            raise OSError(msg)

    def error2(self):
        try:
            LoadLibrary("ABC.DEF.GHI", "activex")
        except OSError as e:
            return str(e)
        else:
            msg = "Did not raise OSError"
            raise OSError(msg)
