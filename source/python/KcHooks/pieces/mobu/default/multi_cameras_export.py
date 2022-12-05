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
import KcLibs.mobu.kc_file_io as kc_file_io
import KcLibs.mobu.kc_model as kc_model
import KcLibs.mobu.kc_camera as kc_camera
TASK_NAME = "camera_export"


def varidate(data, logger, asset_metas):
    return_code = 0

    export_path = data["asset_export_path"]
    if not export_path:
        logger.details.add_detail(u"[error] エクスポートパスを作成できませんでした: {} > {}".format(data["namespace"], export_path))
        logger.debug(u"[error] エクスポートパスを作成できませんでした: {} > {}".format(data["namespace"], export_path))
        logger.details.set_header(1, u"エクスポートパスを作成できませんでした: {}".format(data["namespace"]))
        return {"return_code": 1}
    else:
        logger.details.add_detail(u"エクスポートパスを作成しました: {}".format(export_path))
        logger.debug(u"エクスポートパスを作成しました: {}".format(export_path))

    if not data["config"]["export"]:
        logger.details.add_detail(u"[error] 設定ファイルパスを作成できませんでした: {}".format(data["namespace"]))
        logger.debug(u"[error] 設定ファイルパスを作成できませんでした: {}".format(data["namespace"]))
        logger.details.set_header(1, u"設定ファイルパスを作成できませんでした: {}".format(data["namespace"]))
        return {"return_code": 1}

    if not os.path.exists(data["config"]["export"]):
        logger.details.add_detail(u"[error] 設定ファイルパスが存在しませんでした: {}".format(data["namespace"]))
        logger.debug(u"[error] 設定ファイルパスが存在しませんでした: {}".format(data["namespace"]))
        logger.details.set_header(1, u"設定ファイルパスが存在しませんでした: {}".format(data["namespace"]))
        return {"return_code": 1}
    else:
        logger.details.add_detail(u"設定ファイルパスが存在しました: {}".format(data["config"]["export"]))
        logger.debug(u"設定ファイルパスが存在しました: {}".format(data["config"]["export"]))
    
    logger.details.set_header(0, u"exportできます: {}".format(data["namespace"]))
    return {"return_code": return_code}


def main_export(data, logger, asset_metas, to_master):
    return_code = 0
    kc_model.unselected_all()
    cameras = []
    update_context = {}
    for each in asset_metas:
        if not each["namespace"]:
            model = kc_model.to_object(each["name"])
        else:
            model = kc_model.to_object("{}:{}".format(each["namespace"], each["name"]))

        camera_data = {}
        camera_data["camera"] = model.LongName
        camera_data["width"] = model.ResolutionWidth
        camera_data["height"] = model.ResolutionHeight
        cameras.append(model.LongName)
        # logger.details.add_detail(u"カメラを選択しました: {}".format(model.LongName))
        logger.debug(u"select camera: {}".format(model.LongName))
        model.Selected = True
        if to_master:
            parent = model.Parent
            if parent:
                while not parent:
                    parent = parent.Parent

                m_list = FBModelList()
                if parent:
                    FBGetSelectedModels(m_list, parent, False)
                else:
                    FBGetSelectedModels(m_list, model, False)
                for m in m_list:
                    m.Selected = True
                    logger.debug("select hiararchy models: {}".format(len(m.LongName)))
                    # logger.details.add_detail(u"カメラの階層を選択しました: {}".format(m.LongName))

    kc_file_io.file_save(str(data["asset_export_path"]), selection=True)
    logger.debug(u"exported: {}".format(", ".join(cameras)))
    logger.details.add_detail(u"エクスポートしました: \n{}".format("\n".join(cameras)))

    if data.get("save_switcher", False):
        switcher_data = kc_camera.get_switcher_data(include_object=False)
        if len(switcher_data):
            logger.debug(u"get switcher info: {}".format(switcher_data))
            logger.details.add_detail(u"switcher情報を取得しました: ")
            for each in switcher_data:
                logger.details.add_detail(u"{name} {start} - {end}".format(**each))

        switcher_path = "{}.switcher.json".format(data["asset_export_path"])
        kc_env.save_config(switcher_path,
                           "switcher data",
                           "piece",
                           switcher_data)

        update_context = {"{}.switcher_path".format(TASK_NAME): switcher_path}
    if len(cameras) == 0:
        header = u"カメラがありませんでした"
    else:
        header = u"カメラをエクスポートしました: {}".format(len(cameras))

    logger.details.set_header(return_code, header)
    return {"return_code": return_code, "update_context": update_context}


def main(event={}, context={}):
    data = event.get("data", {})
    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    mode = data.get("mode")

    logger.details.add_detail(u"\nmode: {}\n".format(mode))
    asset_metas = [l for l in data["project"].get_cameras() if l["is_project_asset"]]
    if mode == "varidate":
        return varidate(data, logger, asset_metas)
    elif mode == "master_varidate":
        return varidate(data, logger, asset_metas)
    elif mode == "export":
        return main_export(data, logger, asset_metas, True)
    else:
        return main_export(data, logger, asset_metas, False)


if __name__ == "builtins":
    piece_data = {'path': "E:/works/client/keica/data/assets"}
    data = {
            "namespace": "", 
            "name": "", 
            "category": "camera", 
            "number": 1, 
            "mode": "export"
            }

    data.update(piece_data)
    main({"data": data})
