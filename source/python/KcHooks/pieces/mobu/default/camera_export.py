#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *


sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env

from puzzle2.PzLog import PzLog

TASK_NAME = "camera_export"

def main(event={}, context={}):
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    if not data["category"] == "camera":
        return {"return_code": 0}

    return {"return_code": 0}


if __name__ == "__builtin__":
    piece_data = {'path': "E:/works/client/keica/data/assets"}
    data = {
            "namespace": "", 
            "name": "", 
            "category": "camera", 
            "number": 1
            }

    data.update(piece_data)
    main({"data": data})
