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

_PIECE_NAME_ = "MasterSceneCreate"

class FileMasterSceneCreate(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(MasterSceneCreate, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = ""
        detail = ""

        if not os.path.exists(self.data["master_path"]):
            FBApplication().FileNew()

        else:
            kc_file_io.file_open(self.data["master_path"])
            print "get asset from scene"
            print "check exists"
            print "if not exists.append sotai"

        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":

    piece_data = {'path': "E:/works/client/keica/data/assets"}


    data = {
            "start": 0,
            "end": 100,
            "assets": [{"namespace": "", "name": "", "category": "CH", "number": 1, "sotai_path": ""}, 
                       {"namespace": "", "name": "", "category": "cam", "sotai_path": ""}]
            }

    x = MasterSceneCreate(piece_data=piece_data, data=data)
    x.execute()
