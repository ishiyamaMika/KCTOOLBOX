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

_PIECE_NAME_ = "CameraExport"

class CameraExport(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(CameraExport, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = ""
        detail = ""

        if not self.data["category"] == "cam":
            return flg, self.pass_data, header, detail

        print "select models"
        print "export camera"

        print self.data

        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":

    piece_data = {'path': "E:/works/client/keica/data/assets"}


    data = {
            "namespace": "", 
            "name": "", 
            "category": "cam", 
            "number": 1
            }

    x = CameraExport(piece_data=piece_data, data=data)
    x.execute()
