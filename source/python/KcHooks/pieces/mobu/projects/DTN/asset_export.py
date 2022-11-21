#-*- coding: utf8 -*-

import os
import sys
import json
import re

from pyfbsdk import *

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env

import KcLibs.mobu.kc_model as kc_model
import KcLibs.mobu.kc_file_io as kc_file_io


from puzzle2.PzLog import PzLog
from KcLibs.core.KcProject import *

TASK_NAME = "asset_export"

def varidate(data, logger):
    export_path = data["export_path"]

    if not export_path:
        logger.details.add_detail(u"[error] エクスポートパスを作成できませんでした: {} > {}".format(data["namespace"], export_path))
        logger.debug(u"[error] エクスポートパスを作成できませんでした: {} > {}".format(data["namespace"], export_path))
        return {"return_code": 1}

    if not data["config"]["export"]:
        logger.details.add_detail(u"[error] 設定ファイルパスを作成できませんでした: {}".format(data["namespace"]))
        logger.debug(u"[error] 設定ファイルパスを作成できませんでした: {}".format(data["namespace"]))
        return {"return_code": 1}

    if not os.path.exists(data["config"]["export"]):
        logger.details.add_detail(u"[error] 設定ファイルパスが存在しませんでした: {}".format(data["namespace"]))
        logger.debug(u"[error] 設定ファイルパスが存在しませんでした: {}".format(data["namespace"]))
        return {"return_code": 1}

    asset_directory = os.path.normpath(os.path.join(data["config"]["export"], "../../"))
    paths = data["project"].config["asset"]["mobu"]["paths"]

    if data["category"] == "camera":
        asset_metas = data["project"].get_cameras()
    else:
        asset_metas = [data["project"].get_asset(data["namespace"])]

    take_versions = []
    for each in os.listdir(asset_directory):
        if not each.lower().endswith(".fbx"):
            continue

        asset_path = "{}/{}".format(asset_directory, each)

        if data["category"] in paths:
            template = paths[data["category"]]["rig"]
        else:
            template = paths["default"]["rig"]

        fields = data["project"].path_split(template, asset_path)

        if "<take>" in fields:
            try:
                take_versions.append([int(fields["<take>"]), int(fields["<version>"])])
            except:
                import traceback
                print(traceback.format_exc())
                continue

    take_versions.sort()
    if len(take_versions) == 0:
        logger.details.add_detail(u"[error] アセットファイルが存在しません: {}".format(data["namespace"]))
        logger.debug(u"[error] アセットファイルが存在しません: {}".format(data["namespace"]))
        return {"return_code": 1}

    is_not_same_takes = False
    for asset_meta in asset_metas:
        if "take" not in asset_meta:
            continue
        if asset_meta["take"] != take_versions[-1][0]:
            logger.details.add_detail(u"[error] シーン中のアセットのテイクが違います: {} ({} {}) < ({} {})".format(data["namespace"], int(asset_meta["take"]), int(asset_meta["version"]), take_versions[-1][0], take_versions[-1][1]))
            logger.debug(u"[error] シーン中のアセットのテイクが違います: {} ({} {}) < ({} {})".format(data["namespace"], int(asset_meta["take"]), int(asset_meta["version"]), take_versions[-1][0], take_versions[-1][1]))
            is_not_same_takes = True

    if is_not_same_takes:
        return {"return_code": 1}

    info, models = data["project"].sticky.read(data["config"]["export"])

    model_names = ["{}:{}".format(data["namespace"], l["name"]) for l in models]

    models = kc_model.to_object(model_names) or []


    if len(model_names) != len(models) and data["category"] != "camera":
        diff = list(set(model_names) | set([l.LongName for l in models]))
        logger.details.add_detail(u"[error] 設定ファイルとシーンのモデルの数が違います: {} ({})".format(data["namespace"], len(diff)))
        logger.details.add_detail(u"以下のmodelがありません\n{}".format("\n".join(diff)))
        logger.debug(u"[error] 設定ファイルとシーンのモデルの数が違います: {} ({})".format(data["namespace"], len(diff)))
        return {"return_code": 1}
    if data["category"] == "camera":
        logger.details.add_detail(u"シーン中にあるカメラ: {}".format(",".join([l["name"] for l in asset_metas])))
    else:
        logger.details.add_detail(u"設定ファイルとシーンのモデル数は一致しています: {}".format(data["namespace"]))
        logger.debug(u"設定ファイルとシーンのモデル数は一致しています: {}".format(data["namespace"]))
    return {"return_code": 0}


def master_varidate(data, logger):
    export_path = data["export_path"]
    if not export_path:
        logger.details.add_detail(u"[error] エクスポートパスを作成できませんでした: {} > {}".format(data["namespace"], export_path))
        logger.debug(u"[error] エクスポートパスを作成できませんでした: {} > {}".format(data["namespace"], export_path))
        return {"return_code": 1}

    if not data["config"]["export"]:
        logger.details.add_detail(u"[error] 設定ファイルパスを作成できませんでした: {}".format(data["namespace"]))
        logger.debug(u"[error] 設定ファイルパスを作成できませんでした: {}".format(data["namespace"]))
        return {"return_code": 1}

    if not os.path.exists(data["config"]["export"]):
        logger.details.add_detail(u"[error] 設定ファイルパスが存在しませんでした: {}".format(data["namespace"]))
        logger.debug(u"[error] 設定ファイルパスが存在しませんでした: {}".format(data["namespace"]))
        return {"return_code": 1}

    asset_directory = os.path.dirname(data["max_asset_path"])
    paths = data["project"].config["asset"]["max"]["paths"]
    if data["category"] == "camera":
        asset_metas = data["project"].get_cameras()

    else:
        asset_metas = data["project"].get_asset(data["namespace"])

    is_not_asset_meta_flg = False
    for asset_meta in asset_metas:
        if not asset_meta:
            logger.details.add_detail(u"[error] metaモデルがアセットに設定されていません: {}".format(data["namespace"]))
            logger.debug(u"[error] metaモデルがアセットに設定されていません: {}".format(data["namespace"]))
            is_not_asset_meta_flg = True
    
    if is_not_asset_meta_flg:
        return {"return_code": 1}

    take_versions = []

    for each in os.listdir(asset_directory):
        if not each.lower().endswith(".max"):
            continue

        asset_path = "{}/{}".format(asset_directory, each)

        if data["category"] in paths:
            template = paths[data["category"]]["rig"]
        else:
            template = paths["default"]["rig"]
        
        fields = data["project"].path_split(template, asset_path)
        if "<take>" in fields:
            try:
                take_versions.append([int(fields["<take>"]), int(fields["<version>"])])
            except:
                continue
    
    take_versions.sort()

    if len(take_versions) == 0:
        logger.details.add_detail(u"[error] アセットファイルが存在しません: {}".format(data["namespace"]))
        logger.debug(u"[error] アセットファイルが存在しません: {}".format(data["namespace"]))
        return {"return_code": 1}

    if asset_meta["take"] != take_versions[-1][0]:
        logger.details.add_detail(u"[error] シーン中のアセットのテイクが違います: {} ({} {}) < ({} {})".format(data["namespace"], int(asset_meta["take"]), int(asset_meta["version"]), take_versions[-1][0], take_versions[-1][1]))
        logger.debug(u"[error] シーン中のアセットのテイクが違います: {} ({} {}) < ({} {})".format(data["namespace"], int(asset_meta["take"]), int(asset_meta["version"]), take_versions[-1][0], take_versions[-1][1]))
        return {"return_code": 1}

    info, models = data["project"].sticky.read(data["config"]["export"])
    model_names = ["{}:{}".format(data["namespace"], l["name"]) for l in models if ignore_models(l["name"])]

    models = kc_model.to_object(model_names) or []

    if len(model_names) != len(models):
        diff = list(set(model_names) | set([l.LongName for l in models if ignore_models(l["name"])]))
        logger.details.add_detail(u"[error] 設定ファイルとシーンのモデルの数が違います: {} ({})".format(data["namespace"], len(diff)))
        logger.debug(u"[error] 設定ファイルとシーンのモデルの数が違います: {} ({})".format(data["namespace"], len(diff)))        
        logger.details.add_detail(u"以下のmodelがありません\n{}".format("\n".join(diff)))
        return {"return_code": 1}
    
    logger.details.add_detail(u"設定ファイルとシーンのモデル数は一致しています: {}".format(data["namespace"]))
    logger.debug(u"設定ファイルとシーンのモデル数は一致しています: {}".format(data["namespace"]))
    return {"return_code": 0}


def ignore_models(model_name):
    return True
    ignores = ["_ctrlSpace", "_jtSpace"]
    for ignore in ignores:
        if ignore in model_name:
            return False
    return True

def main_export(data, logger):
    kc_model.unselected_all()
    flg = True
    key_name = "export"
    if "key_name" in data:
        key_name = data["key_name"]

    info, models = data["project"].sticky.read(data["config"][key_name])

    if data["category"] == "camera":
        cameras = []
        for each in data["project"].get_cameras():
            model = kc_model.to_object("{}:{}".format(each["namespace"], each["name"]))
            camera_data = {}
            camera_data["camera"] = model.LongName
            camera_data["width"] = model.ResolutionWidth
            camera_data["height"] = model.ResolutionHeight
            cameras.append(cameras)
            model.Selected = True

        kc_file_io.file_save(str(data["export_path"]), selection=True)

    else:
        model_names = ["{}:{}".format(data["namespace"], l["name"]) for l in models if ignore_models(l["name"])]
        models = kc_model.select(model_names)

        if len(model_names) == len(models):
            logger.debug("models is all selected: {}".format(data["namespace"]))
            kc_file_io.file_save(str(data["export_path"]), selection=True)

        else:
            models_ = set([l.LongName for l in models])
            model_names_ = set(model_names)
            logger.warning("this model is not selected: {}: {}".format(data["namespace"], " ".join(list(model_names_-models_))))

    header = u"ファイルをエクスポートしました: {}".format(data["namespace"])
    detail = u"path: \n{}\nexport key name: {}".format(data["export_path"], key_name)

    logger.details.add_detail(header)
    logger.details.add_detail(detail)
    return {"return_code": 0}


def main(event={}, context={}):
    """
    from setting: piece_data: mode, key_name
    from pass_data: project, @camera, @width, @height
    """
    data = event.get("data", {})
    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0
    logger.debug("mode: {}".format(data.get("mode")))
    if data.get("mode") == "varidate":
        return varidate(data, logger)
    elif data.get("mode") == "master_varidate":
        return master_varidate(data, logger)
    else:
        return main_export(data, logger)





if __name__ in ["__builtin__", "builtins"]:
    x = KcProject()
    x.set("ZIM", "default")
    from KcLibs.core.KcProject import KcProject
    def edit_varidate__test():
        piece_data = {'path': "E:/works/client/keica/data/assets", 
                    "mode": "varidate", 
                    "paint": 
                        {
                            "export_path": "mobu_edit_export_path"}
                        }

        data = {u'category': u'CH',
            'config': {'export': False, 'plot': False},
            'cut': u'001',
            'end': 0,
            'mobu_edit_export_path': u'E:/works/client/keica/_942_ZIZ/3D/s01/c001/master/export/ZIM_s01c001_anim_CH_tsukikoQuad.fbx',
                u'config': {'export': "E:/works/client/keica/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_3D_assets/CH/tsukikoQuad/MB/config/CH_tsukikoQuad_export.json",
                                'plot': "E:/works/client/keica/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/_3D_assets/CH/tsukikoQuad/MB/config/CH_tsukikoQuad_plot.json"},
            'mobu_sotai_path': False,
            u'namespace': u'CH_tsukikoQuad',
            'scene': u'01',
            u'selection': True,
            'start': 0,
            u'take': 2.0,
            u'true_namespace': u'CH_tsukikoQuad',
            u'type': u'both',
            u'update_at': u'2021/11/18 01:17:16',
            u'update_by': u'amek', 
            u"project": x}
        
        data.update(piece_data)
        return data
    
    def master_varidate__test():
        data = {'category': 'camera',
                'config': {'export': 'K:/DTN/LO/Asset_keica/camera/MB/models/cam_s00c000_export.json',
                      'plot': 'K:/DTN/LO/Asset_keica/camera/MB/models/cam_s00c000_plot.json'},
                'cut': 'A9000-A9999',
                'end': 120,
                'export_path': 'K:/DTN/3D/s00/cA9000-A9999/master/export/DTN_s00cA9000-A9999_Cam_AA9000-A9999.fbx',
                'sotai_path': 'K:/DTN/LO/Asset_keica/camera/MB/sotai/cam_sotai_t01.FBX',
                'namespace': 'Cam_A9000-A9999',
                'scene': 0,
                "mode": "varidate",
                'start': 0}

        # data.update(piece_data)
        return data
    data = master_varidate__test()
    x = KcProject()
    x.set("DTN", "default")
    data["project"] = x
    # data["export_path"] = data["mobu_master_export_path"]

    main({"data": data})

