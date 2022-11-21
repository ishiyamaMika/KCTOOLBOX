#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_model as kc_model

from puzzle2.PzLog import PzLog

TASK_NAME = "get_cameras"

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
        is_project_asset = False
        if len(cam_s) == 1:
            namespace = False
        else:
            namespace = cam_s[0]
            meta_model = kc_model.to_object("{}:meta".format(namespace))
            if meta_model:
                meta_property = meta_model.PropertyList.Find("category").Data
                if meta_property == "camera":
                    is_project_asset = True

        if "BirdsView" in each.LongName:
            is_project_asset = True

        elif not namespace:
            continue
        name = each.Name
        if data.get("include_model"):
            cameras.append({"namespace": namespace, "name": name, "model": each, "category": "camera", "is_project_asset": is_project_asset})
        else:
            cameras.append({"namespace": namespace, "name": name, "category": "camera", "is_project_asset": is_project_asset})

    update_context = {}
    update_context["{}.cameras".format(TASK_NAME)] = cameras
    return {"return_code": return_code, "update_context": update_context}


if __name__ in ["__builtin__", "builtins"]:
    piece_data = {"include_model": True}
    data = {}
    data.update(piece_data)

    print(main({"data": data}))
