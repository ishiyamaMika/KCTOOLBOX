# -*- coding: utf8 -*-

import os
import sys

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if mod not in sys.path:
    sys.path.append(mod)

import KcLibs.core.kc_env as kc_env
kc_env.append_sys_paths()

from shotgun_api3 import Shotgun
import shotgun_api3
import yaml
import puzzle.pz_config as pz_config

__CONNECTION__ = {}


def _connect(server, user=None, pwd=None, script_name=None, api=None):
    global __CONNECTION__
    if api is not None:
        if script_name in __CONNECTION__:
            return __CONNECTION__[script_name]

        sg = Shotgun(server, script_name=script_name, api_key=api)
        __CONNECTION__[script_name] = sg
        return sg

    else:
        if user in __CONNECTION__:
            return __CONNECTION__[user]

        sg = Shutgun(server, user=user, password=pwd)
        __CONNECTION__[user] = sg
        return sg


def connect_by_script(script_name="deamon_login"):
    path = "{}/login.yml".format(kc_env.get_app_config("shotgun"))
    info, data = pz_config.read(path)
    if script_name in data:
        info = data[script_name]

    else:
        return False

    return _connect(info["server"], script_name=script_name, api=info["api"])


def get_scene_info(shot_name, script_name="centrum"):
    sg = connect_by_script(script_name)

    find = sg.find_one("Shot", [["code", "is", shot_name]], ["sg_cut_in", 
                                                             "sg_cut_out", 
                                                             "sg_manage_camera.Camera.sg_resolution_x", 
                                                             "sg_manage_camera.Camera.sg_resolution_y", 
                                                             "sg_manage_camera.Camera.sg_use_default_render_size"])
    if not find:
        return False

    dic_info = {}
    dic_info["task_id"] = find["id"]
    dic_info["name"] = shot_name
    dic_info["start_frame"] = find["sg_cut_in"]
    dic_info["end_frame"] = find["sg_cut_out"]
    dic_info["width"] = find["sg_manage_camera.Camera.sg_resolution_x"]
    dic_info["height"] = find["sg_manage_camera.Camera.sg_resolution_y"]
    if find["sg_manage_camera.Camera.sg_use_default_render_size"]:
        dic_info["width"] = 2112
        dic_info["height"] = 1188

    dic_info["default_render_size"] = find["sg_manage_camera.Camera.sg_use_default_render_size"]

    # assets = sg.find("CustomEntity40", [[""]])

    return dic_info

if __name__ == "__main__":
    print get_scene_info("ep00s01c001")
if __name__ == "__main__":
    print connect_by_script("deamon_login")