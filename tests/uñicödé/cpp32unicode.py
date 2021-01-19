# -*- coding: utf-8 -*-
import ctypes

from msl.loadlib import Server32


class Cpp32(Server32):

    def __init__(self, host, port, **kwargs):
        super(Cpp32, self).__init__(u'cpp_lib32-uñicödé', 'cdll', host, port)

    def add(self, a, b):
        return self.lib.add(ctypes.c_int32(a), ctypes.c_int32(b))
