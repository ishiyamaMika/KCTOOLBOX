#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env

import KcLibs.mobu.kc_transport_time as kc_transport_time

from puzzle2.PzLog import PzLog

TASK_NAME = "file_master_create"

def main(event={}, context={}):
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    if not os.path.exists(data["master_path"]):
        FBApplication().FileNew()

    else:
        kc_file_io.file_open(data["master_path"])

    kc_transport_time.set_scene_time(data["start"], 
                                        data["end"], 
                                        data["start"], 
                                        data["end"], 
                                        data["fps"])
    return {"return_code": return_code}

if __name__ == "__builtin__":

    piece_data = {'path': "E:/works/client/keica/data/assets"}

    data = {
            "start": 0,
            "end": 100,
            "assets": [{"namespace": "", "name": "", "category": "CH", "number": 1, "sotai_path": ""}, 
                       {"namespace": "", "name": "", "category": "cam", "sotai_path": ""}]
            }

    data.update(piece_data)
    data["master_path"] = "{}/test.fbx".format(piece_data)
    main({"data": data})
