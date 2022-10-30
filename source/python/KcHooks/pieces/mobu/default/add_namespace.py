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

TASK_NAME = "add_namespace"

def main(event={}, context={}):
    """
    pice_data: force
    """

    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    if "namespace" not in data:
        logger.details.set_header(u"ネームスペースが設定されていません")
        return {"return_code": 1}

    if data["namespace"] == "":
        logger.details.set_header(u"ネームスペースが設定されていません")
        return {"return_code": 1}

    m_list = FBModelList()
    FBGetSelectedModels(m_list)
    for m in m_list:
        m.Selected = False

    for each in FBSystem().Scene.RootModel.Children:
        if each.Name == "Reference":
            continue

        m_list = FBModelList()
        FBGetSelectedModels(m_list, each, False, False)
        for m in m_list:
            if data.get("force", False):
                m.LongName = "{}:{}".format(data["namespace"], m.Name)
                logger.debug("append: {}".format(m.LongName))
            else:
                if ":" in m.LongName:
                    continue
                else:
                    m.LongName = "{}:{}".format(data["namespace"], m.Name)
                    logger.debug("append: {}".format(m.LongName))

    return {"return_code": return_code}


if __name__ in ["builtins", "__builtin__"]:
    piece_data = {"force": True}
    data = {"namespace": "Mia"}
    data.update(piece_data)
    print(main(event={"data": data}))