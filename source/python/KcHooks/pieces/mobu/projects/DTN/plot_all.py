#-*- coding: utf8 -*-

import os
import sys
import json

from pyfbsdk import *

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env
from KcLibs.core.KcProject import KcProject
import KcLibs.mobu.kc_key as kc_key
import KcLibs.mobu.kc_model as kc_model


from puzzle2.PzLog import PzLog

TASK_NAME = "plot_all"


def main(event={}, context={}):
    """
    piece_data: interpolate
    """
    def _ignore(model_name):
        return True
        ignores = ["_ctrlSpace", "_jtSpace"]
        for ignore in ignores:
            if ignore in model_name:
                return False
        return True

    data = event.get("data", {})
    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0
  
    """
    start = data["start"]
    end = data["end"]
    fps = data["project"].config["general"]["fps"]
    """

    cams = data["project"].get_cameras()
    
    model_names = []
    update_context = {}
    for asset in data.get("assets", []):
        if not "config" in asset:
            continue

        config = asset["config"].get("plot")
        logger.debug("config path: {}".format(config))
        if not config:
            continue

        if not os.path.lexists(config):
            continue
        
        info, data_ = data["project"].sticky.read(config)
        if asset["category"] == "camera":
            for cam in cams:
                for d in data_:
                    if not _ignore(d):
                        continue
                    model_names.append("{}:{}".format(cam["namespace"], d["name"]))
        else:
            for d in data_:
                if not _ignore(d):
                    continue
                model_names.append("{}:{}".format(asset["namespace"], d["name"]))
        
        if asset["category"] == "BG":
            for d in data_:
                m = kc_model.to_object("{}:{}".format(asset["namespace"], d["name"]))
                if m:
                    update_context.setdefault("plot_all.BG_models", []).append(m)

    kc_model.select(model_names)

    header = u"plotしました: {}".format(len(model_names))
    detail = "plot:\n" + "\n".join(model_names)
    kc_key.plot_selected()

    logger.details.set_header(header)
    logger.details.add_detail(detail)

    return {"return_code": return_code, "update_context": update_context}


if __name__ == "__builtin__":

    piece_data = {'path': "E:/works/client/keica/data/assets"}


    data = {
            "start": 0,
            "end": 100,
            "assets": [{"namespace": "", "name": "", "category": "CH", "number": 1}, 
                       {"namespace": "", "name": "", "category": "camera"}]
            }
    data.update(piece_data)
    main({"data": data})
