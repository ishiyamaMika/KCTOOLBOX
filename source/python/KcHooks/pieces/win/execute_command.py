#-*- coding: utf8 -*-

import os
import sys
import json
import datetime
import codecs

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)

sys.path.append("{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"]))

from puzzle.Piece import Piece
from puzzle.Puzzle import execute_command

import KcLibs.core.kc_env as kc_env
import yaml

_PIECE_NAME_ = "ExecuteCommad"

class ExecuteCommad(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(ExecuteCommad, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = ""
        detail = ""
        
        if "app_environ" in self.piece_data:
            app = os.environ[self.piece_data["app_environ"]]
        else:
            app = self.piece_data["app"]

        execute_data = {}
        execute_data["data_path"] = self.data["data_path"]
        execute_data["piece_path"] = self.data["piece_path"]
        execute_data["log_name"] = self.data["log_name"]
        execute_data["log_directory"] = self.data["log_directory"]
        execute_data["message_output"] = self.data["message_output"]
        execute_data["pass_path"] = self.data["pass_path"]
        if "order" in self.data:
            execute_data["order"] = ",".join(self.data["order"])

        execute_data["keys"] = self.piece_data["keys"]
        execute_data["sys_path"] = "{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"])
        execute_data["hook_path"] = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
        if "result" in self.data:
            execute_data["result"] = self.data["result"]

        execute_command(app, **execute_data)

        return flg, self.pass_data, header, detail

if __name__ in ["__builtin__", "__main__"]:
    piece_data = {"app": "C:/Program Files/Autodesk/3ds Max 2020/3dsmax.exe", 
                  "keys": "max_import"}

    data = {
            'data_path': 'F:/works/keica/KcToolBox/config/user/log/amek/multi/KcShotManager/puzzle/20211230_164739_data.json',
            'log_directory': 'F:/works/keica/KcToolBox/config/user/log/amek/multi/KcShotManager/log',
            'message_output': 'F:/works/keica/KcToolBox/config/user/log/amek/multi/KcShotManager/message',
            'log_name': 'KcSceneManager',
            'piece_path': 'F:/works/keica/KcToolBox/config/user/log/amek/multi/KcShotManager/puzzle/20211230_164739_piece.json'
        }

    x = ExecuteCommad(piece_data=piece_data, data=data, pass_data={})
    x.execute()
