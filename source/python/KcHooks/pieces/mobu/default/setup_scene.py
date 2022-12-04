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

TASK_NAME = "setup_scene"


def main(event={}, context={}):
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    header = "add light and hide models"
    detail = ""

    for each in [-90, 0, 90, 180]:
        light = FBLight("light_{}".format(each))
        light.Show = True
        light.PropertyList.Find("Type").Data = 1
        light.Rotation = FBVector3d(each, 0, 90)
    
    for each in FBSystem().Scene.RootModel.Children:
        for child in each.Children:
            if not child.Name == "GEO":
                m_list = FBModelList()
                FBGetSelectedModels(m_list, child, False)
                for m in m_list:
                    m.Show = False
    logger.details.set_header(return_code, header)
    logger.details.add_detail(detail)
    return {"return_code": return_code}

if __name__ == "__builtin__":
    data = {
           "namespace": "camera name",
           "width": 1920,
           "height": 1080
            }
    
    main({"data": data})