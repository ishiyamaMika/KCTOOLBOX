#-*- coding: utf8 -*-

import os
import sys
import re

from pyfbsdk import *

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_model as kc_model

from puzzle2.PzLog import PzLog

TASK_NAME = "get_assets"

def main(event={}, context={}):
    """
    pass_data: assets
    """
    def _number(namespace):
        search = re.search(".*_([0-9]*)", namespace)
        if search:
            groups = [l for l in search.groups() if not l == ""]
            if len(groups) > 0:
                return int(groups[0])
        return 1


    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog("test").logger

    return_code = 0

    assets = []
    
    for meta_model in kc_model.find_models_by_name("*:meta"):
        meta_data = {}
        for meta_name in data["meta"]:
            meta_property = meta_model.PropertyList.Find(meta_name)
            if meta_property:
                if meta_name == "namespace":
                    meta_name = "true_namespace"
                meta_data[meta_name] = meta_property.Data
        namespace = meta_model.LongName.split(":")[0]
        meta_data["namespace"] = namespace

        assets.append(meta_data)
        logger.debug("namespace: {}".format(namespace))

    update_context = {}
    update_context["{}.assets".format(TASK_NAME)] = assets

    return {"return_code": return_code, "update_context": update_context}

if __name__ in ["__builtin__", "builtins"]:
    piece_data = {"include_model": True}
    data = {"meta": ["namespace", "version", "take", "category"]}

    data.update(piece_data)
    print(main({"data": data}))