#-*- coding: utf8 -*-

import os
import sys
import random
import datetime

from pyfbsdk import *


sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_model as kc_model

from puzzle2.PzLog import PzLog

TASK_NAME = "asset_add_properties"


def main(event={}, context={}):
    """
    comming from someware: pass_data: parent_name, color
    """
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0


    category = data["properties"]["category"]
    if not "namespace" in data:
        logger.details.set_header(u"namespaceが設定されていません")
        return {"return_code": 1}

    if category in data["parent_name"]:
        parent_name = data["parent_name"][category]
    else:
        parent_name = data["parent_name"]["default"]

    root_model_name = parent_name.replace("<namespace>", data["namespace"])

    model = kc_model.find_model_by_name(parent_name.split(":")[-1], ignore_namespace=True)
    if not model:
        root_models = [l for l in FBSystem().Scene.RootModel.Children]
        model = FBModelNull(parent_name.split(":")[-1])
        for each in root_models:
            model.ConnectSrc(each)
            logger.debug("ConnectSrc: {}".format(each.LongName))

    meta_model = kc_model.find_model_by_name("meta", ignore_namespace=True)
    meta_color = kc_model.find_material_by_name("meta_color")

    if not meta_model:
        meta_model = FBModelCube("meta")
        meta_model.Show = True
        if model:
            model.ConnectSrc(meta_model)

    if not meta_color:
        meta_color = FBMaterial("meta_color")
        meta_model.ConnectSrc(meta_color)

    property_list = {l.Name: l for l in meta_model.PropertyList if l.Name != ""}
    take = -1
    for prop in data["meta"]:
        if not prop in data["properties"]:
            continue

        value = data["properties"][prop]

        if isinstance(value, int):
            create_type = "number"

        elif isinstance(value, float):
            create_type = "double"

        else:
            create_type = "String"
            value = str(value)

        if prop in property_list:
            property_list[prop].Data = value
        else:
            if meta_model.PropertyList.Find(str(prop)):
                meta_model.PropertyList.Find(str(prop)).Data = value
            else:
                kc_model.create_custom_property(meta_model, prop, create_type, value)

        if prop == "take":
            take = value

    if take > 0:
        color = data["color"].get(take, "random")
        if color == "random":
            color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]

        color = [l for l in color]
        if color[0] > 0:
            color[0] = color[0]/255.0
        if color[1] > 0:
            color[1] = color[1]/255.0
        if color[2] > 0:
            color[2] = color[2]/255.0

        prop = meta_color.PropertyList.Find("DiffuseColor")

        if isinstance(prop.Data, FBVector3d):
            prop.Data = FBVector3d(*color)
        else:
            try:
                prop.Data = FBColor(*color)
            except:
                print("set color failed:", color)

    now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    if "update_at" in property_list:
        property_list["update_at"].Data = now
    else:
        kc_model.create_custom_property(meta_model, "update_at", "String", now)

    if "update_by" in property_list:
        property_list["update_by"].Data = kc_env.get_user()
    else:
        kc_model.create_custom_property(meta_model, "update_by", "String", kc_env.get_user())

    return {"return_code": return_code}


if __name__ == "__builtin__":
    data = {
            "namespace": "CH_tsukikoQuad",
            "properties": {"namespace": "CH_tsukikoQuad", 
                           "asset_name": "tsukikoQuad",
                           "variation": "",
                           "take": 2,
                           "version": 2, 
                           "category": "CH"},
            "meta": [
                     "namespace",
                     "asset_name",
                     "variation",
                     "take",
                     "version",
                     "category",
                     "update_at",
                     "update_by"]   
            }
    piece_data = {
            "parent_name": {"camera": "cam_root", "default": "test"},
            "meta_model_name": "<namespace>:meta",
            "color": {
                1: (255, 0, 0),
                2: (0, 255, 0),
                3: (0, 0, 255),
                4: (255, 255, 0),
                5: (0, 255, 255),
                6: (255, 0, 255),
                7: (255, 255, 255),
                8: (0, 0, 0)
                }
            }
    
    data.update(piece_data)

    main({"data": data})

