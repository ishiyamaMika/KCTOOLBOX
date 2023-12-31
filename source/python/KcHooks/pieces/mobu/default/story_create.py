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
import KcLibs.mobu.kc_file_io as kc_file_io


from puzzle2.PzLog import PzLog

TASK_NAME = "story_create"


def main(event={}, context={}):
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0
    detail = ""

    asset_path = str(data["asset_path"])

    exists = False
    if data["category"] == "camera":
        cameras = data["project"].get_cameras()
        for camera in cameras:
            if data["namespace"] == camera["namespace"]:
                exists = True
    else:
        assets = data["project"].get_assets()
        for asset in assets:
            if data["namespace"] == asset["namespace"]:
                exists = True

    # current_constraints = [l for l in FBSystem().Scene.Constraints]

    if not exists:
        if kc_file_io.file_merge(asset_path, str(data["namespace"])):
            logger.debug("\nadd asset: {}".format(os.path.basename(asset_path)))
            logger.details.add_detail(u"\nassetを追加しました\n{}".format(asset_path))
        else:
            logger.warning("\nadd asset failed: {}".format(os.path.basename(asset_path)))
            logger.details.add_detail(u"\nassetを追加できませんでした\n{}".format(asset_path))
            return_code = 1
    else:
        logger.details.add_detail(u"アセットはすでにシーンに存在します")
    

    """
    now_constraints = [l for l in FBSystem().Scene.Constraints]
    # 追加されたコンストレインのチェックを外す
    for const in now_constraints:
        if not const in current_constraints:
            if const.ClassName() in ["FBStoryTrack", "FBCharacter"]:
                continue
        
            if "CharacterSolver" in const.ClassName():
                continue
            
            const.Active = False
            self.logger.debug("constraint off: {}".format(const.LongName))
    """

    for each in FBSystem().Scene.Characters:
        if each.Active:
            each.Active = False

    plot_config_path = data["config"]["plot"]
    if not plot_config_path:
        header = u"設定ファイルがありませんでした: {}".format(data["namespace"])
        detail = u"path: {}".format(plot_config_path)
        logger.debug("config 'plot' is not exists: {}".format(data["namespace"]))
        logger.details.set_header(1, header)
        logger.details.add_detail(detail)
        return {"return_code": 1}

    info, models = data["project"].sticky.read(plot_config_path)
    model_names = ["{}:{}".format(data["namespace"], l["name"]) for l in models]
    track = kc_story.create_story_track(str(data["namespace"]), model_names)

    kc_story.create_clip(track, str(data["asset_export_path"]), offset=data["start"])
    logger.debug("create story clip: {}".format(data["asset_export_path"]))
    logger.details.add_detail(u"\nストーリークリップを作成しました\n{}".format(data["asset_export_path"]))

    logger.details.set_header(0, u"storyのクリップを作成しました: {}".format(data["namespace"]))
    logger.details.add_detail(detail)
    return {"return_code": return_code}

if __name__ == "__builtin__":
    piece_data = {"paint": {
                        "asset_export_path": "mobu_sotai_path"
                        }
                 }
    data = {
           "namespace": "", 
           "name": "", 
           "category": "CH", 
           "number": 1, 
           "asset_export_path": ""
            }

    data = {u'asset_name': u'CH_tsukikoQuad',
           u'category': u'CH',
           u'config': {'export': 'E:/works/client/keica/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_3D_assets/LO/ABCDE/MB/config/CH_tsukikoQuad_export.json',
                       'plot': 'E:/works/client/keica/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_3D_assets/LO/ABCDE/MB/config/LO_ABCDE_asasad_plot.json'},
           'cut': u'001',
           'end': 0,
           'mobu_edit_export_path': u'E:/works/client/keica/_942_ZIZ/3D/s01/c001/master/export/ZIM_s01c001_anim_LO_ABCDE_asasad_02.fbx',
           'mobu_sotai_path': "E:/works/client/keica/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_3D_assets/CH/tsukikoQuad/MB/CH_tsukikoQuad_sotai_t01.fbx",
           u'namespace': u'CH_tsukikoQuad',
           'scene': u'01',
           u'selection': True,
           'start': 0,
           u'take': 0.0,
           u'true_namespace': u'CH_tsukikoQuad',
           u'type': u'both',
           u'update_at': u'2021/11/23 13:33:10',
           u'update_by': u'amek',
           u'variation': u'asasad',
           u'version': 0.0}


    from KcLibs.core.KcProject import *
    FBApplication().FileNew()
    kc_project = KcProject()
    kc_project.set("ZIM", "default")

    pass_data = {"project": kc_project}

    data.update(pass_data)
    main({"data": data})
