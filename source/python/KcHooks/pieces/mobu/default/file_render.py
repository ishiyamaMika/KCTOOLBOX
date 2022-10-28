#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *


mods = ["{}/source/python".format(os.environ["KEICA_TOOL_PATH"]), 
       "{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"])]

for mod in mods:
    if not mod in sys.path:
        sys.path.append(mod)


from puzzle.Piece import Piece

import KcLibs.core.kc_env as kc_env

_PIECE_NAME_ = "FileRender"

class FileRender(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(FileRender, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = ""
        detail = ""

        print("select camera")
        print("set size")

        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":

    piece_data = {}

    data = {
           "mobu_movie_path": "",
           "width": 1920,
           "height": 1080,
           "start": 0,
           "end": 100
            }

    x = FileRender(piece_data=piece_data, data=data)
    x.execute()
