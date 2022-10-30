#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_file_io as kc_file_io

from puzzle2.PzLog import PzLog

TASK_NAME = "rename_namespace"

def main(event={}, context={}):
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    if data["category"] == "camera":
        logger.details.set_header(u"cameraはリネームされません")
        return {"return_code": 1}

    namespace_s = data["namespace"].split("_")
    if not namespace_s[-1].isdigit():
        logger.details.set_header(u"namespaceを変える必要がありません: {}".format(data["namespace"]))
        return {"return_code": 1}

    FBApplication().FileNew()
    kc_file_io.file_open(data["path"])

    for model in FBSystem().Scene.RootModel.Children:
        m_list = FBModelList()
        FBGetSelectedModels(m_list, model, False, True)
        renamed = []
        count = 0
        for m in m_list:
            long_name = m.LongName
            count += 1
            if ":" in long_name:
                long_name_s = long_name.split(":")
                namespace = long_name_s[0]
                namespace_s = namespace.split("_")
                if namespace_s[-1].isdigit():
                    temp = m.LongName
                    m.LongName = "{}:{}".format("_".join(namespace_s[:-1]), m.Name)
                    renamed.append(u"{} -> {}".format(temp, m.LongName))
        
        header = u"namespaceを変更しました: {}({})".format(data["namespace"], len(renamed))
        detail = u"renamed:\n{}".format("\n".join(renamed))
    kc_file_io.file_save(data["path"])

    logger.details.set_header(header)
    logger.details.set_detail(detail)
    return {"return_code": return_code}

if __name__ == "__builtin__":

    piece_data = {}

    data = {
            "path": "X:/Project/_942_ZIZ/3D/s99/c999/master/export/ZIM_s99c999_anim_CH_tsukikoQuad_02.fbx",
            "category": "CH",
            "namespace": "CH_tsukikoQuad_02"
            }

    main({"data": data})
