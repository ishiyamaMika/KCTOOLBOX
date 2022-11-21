#-*- coding: utf8 -*-

import os
import sys
import json
import datetime
import codecs

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env

from puzzle.Puzzle import execute_command

import KcLibs.core.kc_env as kc_env
import yaml


from puzzle2.PzLog import PzLog

TASK_NAME = "execute_command"


def main(event={}, context={}):
    """
    piece_data: app_environ, app, keys
    """
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    if "app_environ" in data:
        app = os.environ[data["app_environ"]]
    else:
        app = data["app"]

    execute_data = {}
    execute_data["data_path"] = data["data_path"]
    execute_data["piece_path"] = data["piece_path"]
    execute_data["log_name"] = data["log_name"]
    execute_data["log_directory"] = data["log_directory"]
    execute_data["message_output"] = data["message_output"]
    execute_data["pass_path"] = data["pass_path"]
    if "order" in data:
        execute_data["order"] = ",".join(data["order"])

    execute_data["keys"] = data["keys"]
    execute_data["sys_path"] = "{}/source/python/KcLibs/site-packages".format(os.environ["KEICA_TOOL_PATH"])
    execute_data["hook_path"] = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
    if "result" in data:
        execute_data["result"] = data["result"]

    execute_command(app, **execute_data)

    return {"return_code": return_code}

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

    data.update(piece_data)
    main({"data": data})

