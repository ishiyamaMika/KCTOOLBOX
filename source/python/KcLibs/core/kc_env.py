# -*- coding: utf8 -*-

import os 
import sys
import datetime
import json
import logging
from logging import getLogger, StreamHandler
from logging.handlers import TimedRotatingFileHandler

mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
print mod        
if not mod in sys.path:
    sys.path.append(mod)



try:
    import KcLibs.core.kc_sentry as kc_sentry
    kc_sentry.load()
    print "load: sentry"
except:
    pass

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

def get_logger(name="KcToolBox", level="DEBUG"):
    logger = getLogger(name)
    logger.setLevel(getattr(logging, level))

    if len(logger.handlers) != 0:
        return logger

    format = "%(asctime)-25s %(levelname)-10s %(module)-15s %(funcName)-25s line:%(lineno)-5s %(message)s"
    formatter = logging.Formatter(format)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    path = get_log_directory(name)
    if not os.path.exists(path):
        os.makedirs(path)

    log_path = "{}/{}.log".format(path, name)
    print log_path
    file_handler = TimedRotatingFileHandler(log_path, when="W0")
    file_handler.setFormatter(formatter)
    
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    logger.kc_name = name

    return logger


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
    """
    TODO: 
        use save config
    """
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

def save_config(path, name, category, data, **kwargs):
    info = {
        "update_by": get_user(),
        "update_at": datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S"),
        "name": name,
        "category": category
    }
    info.update(kwargs)
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    try:
        json.dump({"info": info, "data": data}, open(path, "w"), "utf8", indent=4)
        return True, info, data
    except:
        return False, info, data


if __name__ in ["__builtin__", "__main__"]:
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

    x = get_logger("AAAA")
    x.debug("debug")
    x.info("info")
    x.warning("warning")
    x.critical("critical")
    print dir(x)
    print
    print 
    for handler in x.handlers:
        print handler

