# -*- coding: utf8 -*-

import os
import sys

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_file_io as kc_file_io
import KcLibs.mobu.kc_model as kc_model

kc_env.append_sys_paths()

from pyfbsdk import FBSystem

from puzzle2.PzLog import PzLog

TASK_NAME = "merge_asset"
DATA_KEY_REQUIRED = ["namespace"]

def main(event={}, context={}):
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    exists = False
    for camera in FBSystem().Scene.Cameras:
        if "BirdsView" in camera.LongName:
            exists = True
            break

    if not exists:
        d, f = os.path.split(data["asset_path"])
        f, ext = os.path.splitext(f)
        bird_view_camera = "{}/BirdsView.fbx".format(d)
        if kc_file_io.file_merge(bird_view_camera, namespace=None):
            model = kc_model.find_model_by_name("BirdsView_A0000".format(data["namespace"]))
        if model:
            model.Name = "BirdsView_{}".format(data["namespace"].replace("Cam_", ""))
            logger.details.add_detail(u"add birds view camera: {}".format(model.LongName))
            logger.debug(u"add birds view camera: {}".format(model.LongName))
    else:
        logger.details.add_detail(u"birds view camera already exists")
        logger.debug(u"birds view camera already exists")

    return {"return_code": return_code}


if __name__ == "builtins":
    data = {"namespace": "Cam_A0503"}
    main(event={"data": data})
