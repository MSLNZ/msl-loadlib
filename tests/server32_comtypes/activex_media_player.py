from msl.loadlib import LoadLibrary, Server32

# comtypes on the 32-bit server will try to import numpy
# remove site-packages before importing msl.loadlib.activex
if Server32.is_interpreter():
    _ = Server32.remove_site_packages_64bit()

from msl.loadlib.activex import Application

prog_id = "MediaPlayer.MediaPlayer.1"


class ActiveX(Server32):
    def __init__(self, host: str, port: int) -> None:
        super().__init__(prog_id, "activex", host, port)
        self._a: Application = Application()

    def this(self) -> bool:
        enabled: bool = self.lib.IsSoundCardEnabled()
        return enabled

    def reload(self) -> bool:
        enabled: bool = self._a.load(prog_id).IsSoundCardEnabled()
        return enabled

    @staticmethod
    def load_library() -> bool:
        enabled: bool = LoadLibrary(prog_id, "activex").lib.IsSoundCardEnabled()
        return enabled

    def error1(self) -> str:
        try:
            self._a.load("ABC.DEF.GHI")
        except OSError as e:
            return str(e)
        else:
            msg = "Did not raise OSError"
            raise OSError(msg)

    def error2(self) -> str:
        try:
            _ = LoadLibrary("ABC.DEF.GHI", "activex")
        except OSError as e:
            return str(e)
        else:
            msg = "Did not raise OSError"
            raise OSError(msg)
