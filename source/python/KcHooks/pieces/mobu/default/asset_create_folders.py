#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_group as kc_group

from puzzle2.PzLog import PzLog

TASK_NAME = "asset_create_folders"

def main(event={}, context={}):
    def _is_in_folder(item):
        if len([i for i in range(item.GetDstCount()) if isinstance(item.GetDst(i), FBFolder) and item.GetDst(i).Name != "Constraints"]) == 0:
            return False
        return True

    def _create_folder(name, item):
        return FBFolder(str(name), item)

    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    categories = {
        "Constraints": "<asset_name>_con",
        "Materials": "<asset_name>_mat",
        "VideoClips": "<asset_name>_vid",
        "Textures": "<asset_name>_tx",
        "Shaders": "<asset_name>_sha"
    }

    folders = {l.Name: l for l in FBSystem().Scene.Folders}

    ignore_type = ["ORCharacterSolver_HIK", "FBCharacter"]
    ignore_name = ["Default Shader"]
    for category in categories.keys():
        name = categories[category].replace("<asset_name>", data["asset_name"])
        items = []

        for each in getattr(FBSystem().Scene, category):
            if each.ClassName() in ignore_type:
                continue

            if each.LongName in ignore_name:
                continue

            if _is_in_folder(each):
                continue

            items.append(each)

        if len(items) > 0:
            if name in folders:
                folder = folders[name]
            else:
                item = items.pop(0)
                folder = _create_folder(name, item)

            for item in items:
                folder.ConnectSrc(item)

    return {"return_code": return_code}

if __name__ == "__builtin__":
    data = {"asset_name": "Mia"}
    piece_data = {
          "groups": [
                {"template": "<asset_name>_top"},
                {"template": "<asset_name>_top/<asset_name>_geo",
                 "category": "geometry"},
                {"template": "<asset_name>_top/<asset_name>_skl", 
                 "category": "skeleton"},
                {"template": "<asset_name>_top/<asset_name>_plot"},
                {"template": "<asset_name>_top/<asset_name>_export"},
                {"template": "<asset_name>_topABC/<asset_name>_exporta/AAAAA", 
                 "category": "others"}
                ]
            }
    
    data.update(piece_data)
    print(main({"data": data}))
