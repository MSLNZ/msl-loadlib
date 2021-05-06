# Changes to ctypes in Python 3.7.6 and 3.8.1 caused the following exception
#   TypeError: item 1 in _argtypes_ passes a union by value, which is unsupported.
# when loading some COM objects, see https://bugs.python.org/issue16575
#
# Want to make sure that the Python interpreter that the server32-windows.exe
# is running on does not raise this TypeError
import os
import sys
import tempfile

from msl.loadlib import Server32


class FileSystemObjectServer(Server32):

    def __init__(self, host, port, **kwargs):

        # comtypes will try to import numpy to see if it is available.
        # Since Client64 passes its sys.path to Server32 the modules that
        # are available to Client64 to import are also available to Server32.
        # Therefore, we don't want this test to fail because the Python
        # environment that is running Client64 has numpy installed.
        # (This only appeared to be an issue when Client64 runs on Python 3.5)
        path = Server32.remove_site_packages_64bit()

        super(FileSystemObjectServer, self).__init__('Scripting.FileSystemObject', 'com', host, port)

        # put 'site-packages' back in
        if path:
            sys.path.append(path)

        self.temp_file = os.path.join(tempfile.gettempdir(), 'msl-loadlib-FileSystemObject.txt')

    def get_temp_file(self):
        return self.temp_file

    def create_and_write(self, text):
        fp = self.lib.CreateTextFile(self.temp_file)
        fp.WriteLine(text)
        fp.Close()
