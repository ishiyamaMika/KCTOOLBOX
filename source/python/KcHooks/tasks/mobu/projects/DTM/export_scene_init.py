# -*-coding: utf8-*-

import sys
import os
import re

from pyfbsdk import *

sys_path = os.path.normpath("{}/source/python".format(os.environ["KEICA_TOOL_PATH"])).replace("\\", "/")

if sys_path not in sys.path:
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_model as kc_model
import KcLibs.mobu.kc_camera as kc_camera

kc_env.append_sys_paths()

TASK_NAME = "export_scene_init"
from puzzle2.PzLog import PzLog

def main(event={}, context={}):
    data = event.get("data", {})
    logger = context.get("logger")    

    if not logger:
        logger = PzLog().logger
    
    models = kc_model.get_root_models()
    model_set = {}
    models = []
    x = []
    for model in FBSystem().Scene.RootModel.Children:
        if isinstance(model, FBCamera):
            continue

        if "Geo_Root" in model.LongName:
            model_set[model.LongName.replace("_Geo_Root", "")] = {"Geo_Root": model}
        else:
            models.append(model)
        x.append(model.LongName)
    
    x.sort()

    keys = list(model_set.keys())
    for key in keys:
        print("")
        print("{}----------------------------------".format(key))
        for model in models:
            if key in model.LongName:
                print(key, model.LongName)
    
        """
        model_name_s = model.LongName.split("_")
        print(model_name_s)
        try:
            print(model_name_s[4], "-----------------------")
        except:
            pass
        if len(model_name_s) > 4 and (re.match(model_name_s[4], "[a-z][A-Z]{1}") or re.match(model_name_s[4], "[a-z][A-Z]{1} [0-9]{1}")):
            index = 4
        else:
            index = 3
        id_ = tuple(model_name_s[:index])
        print(index, ">>>>", id_)
        category = "_".join(model_name_s[index:])
        model_set.setdefault(id_, {})
        model_set[id_][category] = model

        print(model.LongName.split("_")[:index], model.LongName)
        """
    return
    
    switcher_data = kc_camera.get_switcher_data()
    cams = kc_camera.get_all()


if __name__ == "__builtin__":
    main()