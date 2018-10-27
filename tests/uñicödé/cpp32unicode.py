# -*- coding: utf-8 -*-
import ctypes

from msl.loadlib import Server32


class Cpp32(Server32):

    def __init__(self, host, port, quiet, **kwargs):
        Server32.__init__(self, u'cpp_lib32-uñicödé.dll', 'cdll', host, port, quiet)

    def add(self, a, b):
        return self.lib.add(ctypes.c_int32(a), ctypes.c_int32(b))
