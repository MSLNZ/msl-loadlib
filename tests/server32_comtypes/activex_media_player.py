from msl.loadlib import LoadLibrary, Server32

# comtypes on the 32-bit server will try to import numpy
# remove site-packages before importing msl.loadlib.activex
if Server32.is_interpreter():
    Server32.remove_site_packages_64bit()

from msl.loadlib.activex import Application

prog_id = 'MediaPlayer.MediaPlayer.1'


class ActiveX(Server32):

    def __init__(self, host, port, **kwargs):
        super(ActiveX, self).__init__(prog_id, 'activex', host, port)

    def this(self):
        return self.lib.IsSoundCardEnabled()

    def static(self):
        return Application.load(prog_id).IsSoundCardEnabled()

    def create(self):
        return Application().load(prog_id).IsSoundCardEnabled()

    def parent(self):
        app = Application()
        return app.load(prog_id, parent=app).IsSoundCardEnabled()

    def panel(self):
        app = Application()
        panel = app.create_panel()
        return app.load(prog_id, parent=panel).IsSoundCardEnabled()

    def load_library(self):
        return LoadLibrary(prog_id, 'activex').lib.IsSoundCardEnabled()

    def error1(self):
        try:
            Application.load('ABC.DEF.GHI')
        except OSError as e:
            return str(e)
        else:
            raise OSError('Did not raise OSError')

    def error2(self):
        try:
            LoadLibrary('ABC.DEF.GHI', 'activex')
        except OSError as e:
            return str(e)
        else:
            raise OSError('Did not raise OSError')
