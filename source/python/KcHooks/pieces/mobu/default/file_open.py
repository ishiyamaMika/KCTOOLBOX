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
import KcLibs.mobu.kc_transport_time as kc_transport_time

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
        file_path = "new"
        if self.piece_data.get("new"):
            FBApplication().FileNew()
            if self.logger: 
                self.logger.debug("file new")

        current_path = file_io.get_file_path()

        if os.path.normpath(current_path).lower() == os.path.normpath(self.data["path"]).lower() and not self.piece_data.get("force", False):
            self.logger.debug("file was already opened: {}".format(self.data["path"]))
            return flg, self.pass_data, u"開いているファイルが同じです: {}".format(os.path.basename(self.data["path"])), "file name:\n{}".format(self.data["path"])

        if file_io.file_open(self.data["path"]):
            if self.logger: 
                self.logger.debug("file open: {}".format(self.data["path"]))
                file_path = self.data["path"]

        else:
            if self.logger: 
                self.logger.debug("file open failed: {}".format(self.data["path"]))
            flg = False
        
        if "start" in self.data and "end" in self.data and "fps" in self.data:
            self.logger.debug("{} {} {}".format(self.data["start"], self.data["end"], self.data["fps"]))
            kc_transport_time.set_scene_time(loop_start=self.data["start"], 
                                             loop_stop=self.data["end"], 
                                             zoom_start=self.data["start"], 
                                             zoom_stop=self.data["end"], 
                                             fps=self.data["fps"])

        return flg, self.pass_data, u"ファイルを開きました: {}".format(os.path.basename(self.data["path"])), "file name:\n{}".format(file_path)

if __name__ == "__builtin__":

    piece_data = {}

    data = {"path": "E:/works/client/keica/data/assets/Mia.v1.1.fbx"}


    x = FileOpen(piece_data=piece_data, data=data)
    x.execute()
