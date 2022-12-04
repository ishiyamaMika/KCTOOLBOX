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

TASK_NAME = "camera_setup"

def main(event={}, context={}):
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0
    detail = ""
    if "camera" in data:
        camera = kc_model.to_object(str(data["camera"]))

        if camera:
            camera.ResolutionWidth = data["width"]
            camera.ResolutionHeight = data["height"]
            header = u"カメラの解像度を設定しました: {}x{}".format(data["width"], 
                                                                data["height"])

            # camera.ApertureMode = FBCameraApertureMode.kFBApertureHorizontal
            camera.FilmAspectRatio = float(data["width"])/data["height"]
            FBSystem().Scene.Evaluate()
        else:
            header = u"カメラがありませんでした: {}".format(data["camera"])

    else:
        header = u"カメラの解像度を設定できませんでした"
        # detail = data

    logger.details.set_header(return_code, header)
    logger.details.add_detail(detail)
    return {"return_code": return_code}

if __name__ == "__builtin__":

    piece_data = {}

    data = {
           "namespace": "test",
           "width": 1920,
           "height": 1080,
           "camera": "cam_s00c000:Merge_Camera"
            }

    print(main({"data": data}))
