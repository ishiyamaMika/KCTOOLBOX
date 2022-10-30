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

TASK_NAME = "get_cameras"
DATA_KEY_REQUIRED = [""]

def main(event={}, context={}):
    """
    piece_data: include_model
    """
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    cameras = []
    for each in FBSystem().Scene.Cameras:
        if each.SystemCamera:
            continue
        cam_s = each.LongName.split(":")
        if len(cam_s) == 1:
            namespace = False
        else:
            namespace = cam_s[0]

        if not namespace:
            continue

        name = each.Name
        if data.get("include_model"):
            cameras.append({"namespace": namespace, "name": name, "model": each, "category": "camera"})
        else:
            cameras.append({"namespace": namespace, "name": name, "category": "camera"})

    update_context = {}
    update_context["{}.cameras".format(TASK_NAME)] = cameras
    return {"return_code": return_code}


if __name__ == "__builtin__":
    piece_data = {"include_model": True}
    data = {}
    data.update(piece_data)

    main({"data": data})

