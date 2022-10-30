#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *


sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_story as kc_story


from puzzle2.PzLog import PzLog

TASK_NAME = "adjust_scene_assets"
DATA_KEY_REQUIRED = ["project"]

def main(event={}, context={}):
    """
    project(KcProject): 
    """
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    assets = data["project"].get_assets()
    scene_assets = set([l["namespace"] for l in assets if not l["category"] == "camera"])
    config_assets = set([l["namespace"] for l in data["assets"] if not l["category"] == "camera"])

    tracks = {l.Name: l for l in kc_story.get_tracks()}
    models = {}
    for each in FBSystem().Scene.RootModel.Children:
        m_list = FBModelList()
        FBGetSelectedModels(m_list, each, False)
        if ":" in each.LongName:
            each_s = each.LongName.split(":")
            namespace = ":".join(each_s[:-1])
        else:
            continue

        models[namespace] = [l for l in m_list]
        if namespace in tracks:
            models[namespace].append(tracks[namespace])

    for each in FBSystem().Scene.Characters:
        for i in range(each.PropertyList.Find("HipsLink").GetSrcCount()):
            skl = each.PropertyList.Find("HipsLink").GetSrc(i)
            namespace = ":".join(skl.LongName.split(":")[:-1])
            models.setdefault(namespace, [])
            models[namespace].append(each)

    i = 0

    keep = scene_assets & config_assets
    keep = []
    logger.debug("keep assets: {}".format(",".join(keep)))

    for namespace in scene_assets:
        if namespace in keep:
            continue

        if namespace in models:
            logger.details.add_detail("delete namespace: {}\n".format(namespace))
            for model in models[namespace][::-1]:
                name = model.LongName
                type_name = model.ClassName()
                try:
                    model.FBDelete()
                    i += 1
                    logger.details.add_detail("({}){}\n".format(type_name, name))

                except:
                    import traceback
                    logger.warning(traceback.format_exc())
                    logger.details.add_detail("delete failed: {}".format(model.LongName))

    if i == 0:
        logger.details.set_header(u"削除するものはありません")

    else:
        logger.details.set_header(u"不要なアセットを削除しました: {}".format(i))

    return {"return_code": return_code}

if __name__ == "__builtin__":
    piece_data = {'path': "E:/works/client/keica/data/assets"}
    data =  {
        "path": "X:/Project/_942_ZIZ/3D/s99/c999/master/ZIM_s99c999_anim.fbx", 
        "assets": [
            {
                "category": "CH", 
                "selection": True, 
                "namespace": "CH_tsukikoQuad_03", 
                "update_at": "2022/01/07 17:21:03", 
                "variation": "", 
                "asset_name": "tsukikoQuad", 
                "version": 1.0, 
                "take": 6.0, 
                "update_by": "Naoki.ito", 
                "type": "config", 
                "true_namespace": "CH_tsukikoQuad"
            }, 
            {
                "category": "CH", 
                "selection": True, 
                "namespace": "CH_tsukikoQuad_04", 
                "update_at": "2022/01/07 17:21:03", 
                "variation": "", 
                "asset_name": "tsukikoQuad", 
                "version": 1.0, 
                "take": 6.0, 
                "update_by": "Naoki.ito", 
                "type": "config", 
                "true_namespace": "CH_tsukikoQuad"
            },             
            {
                "category": "camera", 
                "namespace": "cam_s99c999", 
                "take": 8.0
            }
        ]
    }

    from KcLibs.core.KcProject import KcProject
    x = KcProject()
    x.set("ZIZ", "default")

    pass_data = {"project": x}
    data.update(pass_data)
    print(main({"data": data, "task": piece_data}))
