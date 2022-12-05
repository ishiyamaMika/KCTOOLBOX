#-*- coding: utf8 -*-

import os
import sys
import json
import re
import glob
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
    export_path = data["asset_export_path"]
    return_code = 0

    if not export_path:
        logger.details.add_detail(u"[error] エクスポートパスを作成できませんでした: {} > {}".format(data["namespace"], export_path))
        logger.debug(u"[error] エクスポートパスを作成できませんでした: {} > {}".format(data["namespace"], export_path))
        logger.details.set_header(1, u"エクスポートパスを作成できませんでした: {} > {}".format(data["namespace"], export_path))
        return {"return_code": 1}

    if not data["asset_export_config_path"]:
        logger.details.add_detail(u"[error] 設定ファイルパスを作成できませんでした: {}".format(data["namespace"]))
        logger.debug(u"[error] 設定ファイルパスを作成できませんでした: {}".format(data["namespace"]))
        logger.details.set_header(1, "[error] 設定ファイルパスを作成できませんでした: {}".format(data["namespace"]))
        return {"return_code": 1}

    if not os.path.exists(data["asset_export_config_path"]):
        logger.details.add_detail(u"[error] 設定ファイルパスが存在しませんでした: {}".format(data["namespace"]))
        logger.debug(u"[error] 設定ファイルパスが存在しませんでした: {}".format(data["namespace"]))
        logger.details.set_header(1, u"設定ファイルパスが存在しませんでした: {}".format(data["namespace"]))
        return {"return_code": 1}

    asset_directory = os.path.normpath(os.path.join(data["asset_export_config_path"], "../../"))
    paths = data["project"].config["asset"]["mobu"]["paths"]

    if data["category"] == "camera":
        asset_metas = data["project"].get_cameras()
    else:
        asset_metas = [data["project"].get_asset(data["namespace"])]

    fields = data["project"].path_split(data["asset_dependency_paths"]["asset_rig_path"], data["asset_rig_path"])
    current_take, current_version = fields["<take>"], fields["<version>"]
    fields["take"] = "*"
    fields["version"] = "*"
    template_path = data["project"].path_generate(data["asset_dependency_paths"]["asset_rig_path"], fields)
    take_versions = []
    for f in glob.glob(template_path):
        f = f.replace("\\", "/")
        group = re.match(template_path.replace("*", "(.*)"), f, re.IGNORECASE)
        if group:
            group = [l for l in group.groups() if l.isdigit()]
            if len(group) == 2:
                take_versions.append(group)

    take_versions.sort()
    latest_take, latest_version = -1, -1
    if len(take_versions) > 0:
        latest_take, latest_version = take_versions[-1]

    if int(latest_take) != int(data["take"]):
        logger.details.add_detail(u"[error] シーン中のアセットのテイクが違います: {} scene: {} < latest: {}".format(data["namespace"], int(current_take), int(latest_take)))
        logger.debug(u"[error] シーン中のアセットのテイクが違います: {} scene: {} < latest: {}".format(data["namespace"], int(current_take), int(latest_take)))
        logger.details.set_header(1, u"シーン中のアセットのテイクが違います: {} scene: {} < latest: {}".format(data["namespace"], int(current_take), int(latest_take)))
        return {"return_code": 1}
    else:
        logger.details.add_detail(u"シーン中のアセットのテイク: {} scene: {}".format(data["namespace"], int(current_take)))

    info, models = data["project"].sticky.read(data["asset_export_config_path"])
    logger.debug("open export config path: {}".format(data["asset_export_config_path"]))

    model_names = ["{}:{}".format(data["namespace"], l["name"]) for l in models]
    models = kc_model.to_object(model_names) or []

    logger.debug("config models count: {}".format(len(model_names)))
    logger.debug("scene models count : {}".format(len(models)))

    if len(model_names) != len(models) and data["category"] != "camera":
        diff = list(set(model_names) | set([l.LongName for l in models]))
        logger.details.add_detail(u"[error] 設定ファイルとシーンのモデルの数が違います: {} ({})".format(data["namespace"], len(diff)))
        logger.details.add_detail(u"以下のmodelがありません\n{}".format("\n".join(diff)))
        logger.debug(u"[error] 設定ファイルとシーンのモデルの数が違います: {} ({})".format(data["namespace"], len(diff)))
        logger.details.set_header(1, u"設定ファイルとシーンのモデルの数が違います: {} ({})".format(data["namespace"], len(diff)))
        return {"return_code": 1}
    if data["category"] == "camera":
        logger.details.add_detail(u"シーン中にあるカメラ: {}".format(",".join([l["name"] for l in asset_metas])))
    else:
        logger.details.add_detail(u"設定ファイルとシーンのモデル数は一致しています: {}".format(data["namespace"]))
        logger.debug(u"設定ファイルとシーンのモデル数は一致しています: {}".format(data["namespace"]))
    
    logger.details.set_header(return_code, u"exportできます: {}".format(data["namespace"]))
    return {"return_code": return_code}


def main_export(data, logger):
    kc_model.unselected_all()
    return_code = 0
    # open plot model list
    asset_plot_path = data["asset_plot_config_path"]
    info, models = data["project"].sticky.read(asset_plot_path)

    if data["category"] == "camera":
        # save all camera
        cameras = []
        for each in data["project"].get_cameras():
            model = kc_model.to_object("{}:{}".format(each["namespace"], each["name"]))
            camera_data = {}
            camera_data["camera"] = model.LongName
            camera_data["width"] = model.ResolutionWidth
            camera_data["height"] = model.ResolutionHeight
            cameras.append(cameras)
            model.Selected = True

        if kc_file_io.file_save(str(data["asset_export_path"]), selection=True):
            logger.debug("camera export: {}".format(data["asset_export_path"]))
            logger.details.add_detail("camera export: {}\n".format(data["asset_export_path"]))
            header = u"exportしました: \n{}".format(os.path.basename(data["asset_export_path"]))
        else:
            logger.warning("camera export failed: {}".format(data["asset_export_path"]))
            logger.details.add_detail("camera export failed: {}\n".format(data["asset_export_path"]))
            header = u"exportに失敗しました: \n{}".format(os.path.basename(data["asset_export_path"]))
            return_code = 1

    else:
        # select models and save
        model_names = ["{}:{}".format(data["namespace"], l["name"]) for l in models]
        models = kc_model.select(model_names)

        if len(model_names) == len(models):
            logger.debug("models is all selected: {}".format(data["namespace"]))
            if kc_file_io.file_save(str(data["asset_export_path"]), selection=True):
                logger.debug("model export: {}".format(data["asset_export_path"]))
                logger.details.add_detail(u"エクスポートファイル: \n{}".format(data["asset_export_path"]))
                header = u"exportしました: {}".format(os.path.basename(data["asset_export_path"]))
            else:
                logger.warning("model export failed: {}".format(data["asset_export_path"]))
                logger.details.add_detail(u"エクスポートに失敗しました: \n{}".format(data["asset_export_path"]))
                header = u"exportに失敗しました: {}".format(os.path.basename(data["asset_export_path"]))
                return_code = 1

        else:
            models_ = set([l.LongName for l in models])
            model_names_ = set(model_names)
            logger.warning("this model is not selected: {}: {}".format(data["namespace"], " ".join(list(model_names_-models_))))
    logger.details.set_header(return_code, header)
    return {"return_code": return_code}


def main(event={}, context={}):
    """
    from setting: piece_data: mode, key_name
    from pass_data: project, @camera, @width, @height
    """
    data = event.get("data", {})
    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    logger.debug("mode: {}".format(data.get("mode")))
    if data.get("mode") == "varidate":
        return varidate(data, logger)
    else:
        return main_export(data, logger)


if __name__ in ["__builtin__", "builtins"]:

    from KcLibs.core.KcProject import KcProject
    x = KcProject()
    x.set("DTN", "default")
    data = {'asset_dependency_paths': {'asset_export_config_path': '<asset_root>/<category>/models/PROPS_<asset_name>_export.json',
                                        'asset_plot_config_path': '<asset_root>/<category>/models/PROPS_<asset_name>_plot.json',
                                        'asset_rig_path': '<asset_root>/<category>/PROPS_<asset_name>_t<take>_<version>.fbx',
                                        'asset_sotai_path': '<asset_root>/<category>/sotai/PROPS_<asset_name>_sotai_t<take>.fbx',
                                        'shot_edit_export_path': '<shot_root>/<part>_<seq>/<part>_<seq>_<cut>/master/export/<project>_<seq>_<cut>_anim_<namespace>.fbx'},
            'asset_export_config_path': 'K:/DTN/LO/Asset_keica/PROPS/models/PROPS_HAM_Sword_A_export.json',
            'asset_export_path': 'K:/DTN/LO/A_S99/A_S99_A9000-A9002/master/export/DTN_S99_A9000-A9002_anim_PROPS_HAM_Sword_A.fbx',
            'asset_name': 'HAM_Sword_A',
            'asset_plot_config_path': 'K:/DTN/LO/Asset_keica/PROPS/models/PROPS_HAM_Sword_A_plot.json',
            'category': 'PROPS',
            'config': {'export': 'K:/DTN/LO/Asset_keica/PROPS/models/PROPS_HAM_Sword_A_export.json',
                        'plot': 'K:/DTN/LO/Asset_keica/PROPS/models/PROPS_HAM_Sword_A_plot.json'},
            'cut': 'A9000-A9002',
            'end': 120,
            'mode': 'varidate',
            'namespace': 'PROPS_HAM_Sword_A',
            'part': 'A',
            'progress': 'anim',
            'project': x,
            'root_directory': 'K:/DTN',
            'scene': 0,
            'selection': True,
            'seq': 'S99',
            'shot_root': 'K:/DTN/LO',
            'start': 0,
            'take': '01',
            'true_namespace': 'PROPS_HAM_Sword_A',
            'type': 'both',
            'update_at': '2022/11/04 17:26:45',
            'update_by': 'sasou',
            'user': 'amek',
            "asset_rig_path": "K:/DTN/LO/Asset_keica/PROPS/PROPS_HAM_Sword_A_t01_01.fbx",
            'version': '01'}

    main({"data": data})

