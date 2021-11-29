#-*- coding: utf8 -*-

import os
import sys
import json
import pprint

from pyfbsdk import *


mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

sys.path.append("{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"]))

from puzzle.Piece import Piece

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_file_io as file_io
reload(file_io)
_PIECE_NAME_ = "FileOpen"

class FileOpen(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(FileOpen, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = ""
        detail = ""
        if self.piece_data.get("new"):
            FBApplication().FileNew()
            if self.logger: self.logger.debug("file new")

        if file_io.file_open(self.data["path"]):
            if self.logger: self.logger.debug("file open: {}".format(self.data["path"]))
        else:
            if self.logger: self.logger.debug("file open failed: {}".format(self.data["path"]))
            flg = False

        return flg, self.pass_data, header, detail

if __name__ == "__builtin__":

    piece_data = {}

    data = {"path": "E:/works/client/keica/data/assets/Mia.v1.1.fbx"}


    x = FileOpen(piece_data=piece_data, data=data)
    x.execute()
