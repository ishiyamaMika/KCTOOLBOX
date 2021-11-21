# -*- coding: utf8 -*-

import os 
import sys
import datetime
import json

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
print mod        
if not mod in sys.path:
    sys.path.append(mod)



if os.environ["USERNAME"] == "ame_k":
    import KcLibs.core.kc_sentry as kc_sentry
    kc_sentry.load()

mode = None
try:
    import maya.cmds as cmds
    mode = "maya"
except:
    pass

if mode is None:
    try:
        import MaxPlus
        mode = "3dsmax"
    except:
        pass

if mode is None:
    try:
        from pyfbsdk import FBApplication
        mode = "mobu"
    except:
        pass

if mode is None:
    mode = "win"

def get_root_directory():
    return os.environ["KEICA_TOOL_PATH"].replace("\\", "/")

def append_sys_paths():
    sys_paths = ["{}/source/python/KcLibs/site-packages".format(get_root_directory())]
    for sys_path in sys_paths:
        if sys_path not in sys.path:
            sys.path.append(sys_path)

    return sys_paths

def get_user():
    return os.environ.get("KEICA_USERNAME", os.environ["USERNAME"]).replace("_", "")


def get_app_config(*args):
    joined = "/".join(args)
    return "{}/config/apps/{}".format(get_root_directory(), joined)


def get_tool_config(*args):
    joined = "/".join(args)
    return "{}/source/python/KcTools/{}".format(get_root_directory(), joined)


def get_user_config(*args):
    joined = "/".join(args)
    return "{}/config/user/{}/{}".format(get_root_directory(), get_user(), joined)    


def get_log_directory(*args):
    joined = "/".join(args)
    return "{}/config/user/log/{}/{}".format(get_root_directory(), get_user(), joined)

def get_info(**kwargs):
    info = {"update_by": get_user(), 
            "update_at": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")}

    info.update(kwargs)
    return info

def load_config(path, defaults={}):
    if os.path.lexists(path):
        try:
            js = json.load(open(path, "r"), "utf8")
            data = js["data"]
        except:
            data = {}
    else:
        data = {}

    for k, v in defaults.items():
        data.setdefault(k, v)
    return data

def save_config(path, name, category, data):
    info = {
        "user": get_user(),
        "update_at": datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S"),
        "name": name,
        "category": category
    }
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    try:
        json.dump({"info": info, "data": data}, open(path, "w"), "utf8", indent=4)
        return True
    except:
        return False


if __name__ == "__main__":
    def get_root_directory_test():
        print get_root_directory()

    def append_sys_paths_test():
        print append_sys_paths()

    def get_app_config_test():
        print get_app_config("Ksubmitter")

    def get_user_config_test():
        print get_user_config("Ksubmitter", "ui_config.json")

    def get_log_directory_test():
        print get_log_directory("Ksubmitter", "main.log")


    get_root_directory_test()
    append_sys_paths_test()
    get_app_config_test()
    get_user_config_test()
    get_log_directory_test()

