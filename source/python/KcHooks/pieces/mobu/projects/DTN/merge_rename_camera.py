# -*- coding: utf8 -*-

import os
import sys

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_file_io as kc_file_io
import KcLibs.mobu.kc_model as kc_model

kc_env.append_sys_paths()

from puzzle2.PzLog import PzLog

TASK_NAME = "merge_asset"
DATA_KEY_REQUIRED = ["namespace"]

def main(event={}, context={}):
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    model = kc_model.find_model_by_name("{}:Cam_A0000".format(data["namespace"]))
    if model:
        model.Name = data["namespace"]

    return {"return_code": return_code}

if __name__ == "builtins":
    data = {"namespace": "Cam_A0503"}
    main(event={"data": data})
