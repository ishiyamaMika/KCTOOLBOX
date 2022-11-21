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
import KcLibs.mobu.kc_file_io as file_io
import KcLibs.mobu.kc_transport_time as kc_transport_time


from puzzle2.PzLog import PzLog

TASK_NAME = "file_open"

def get_time():
    return kc_transport_time.get_scene_time()

def main(event={}, context={}):
    """
    piece_data: new, force

    """
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    logger.details.get_all()
    return_code = 0

    file_path = "new"
    update_context = {}
    if data.get("new"):
        FBApplication().FileNew()
        logger.debug("file new")
    else:
        current_path = file_io.get_file_path()

        if os.path.normpath(current_path).lower() == os.path.normpath(data["path"]).lower() and not data.get("force", False):
            logger.debug("file was already opened: {}".format(data["path"]))
            logger.details.set_header(u"開いているファイルが同じです: {}".format(os.path.basename(data["path"])))
            logger.details.add_detail("file name:\n\n{}".format(data["path"]))
            update_context = {"{}.scene_times".format(TASK_NAME): get_time()}
            return {"return_code": return_code, "update_context": update_context}

        if file_io.file_open(data["path"]):
            logger.debug("file open: {}".format(data["path"]))
            file_path = data["path"]
            update_context = {"{}.scene_times".format(TASK_NAME): get_time()}

        else:
            logger.debug("file open failed: {}".format(data["path"]))
            return_code = 1

    if "start" in data and "end" in data and "fps" in data:
        logger.debug("{} {} {}".format(data["start"], data["end"], data["fps"]))
        kc_transport_time.set_scene_time(loop_start=data["start"],
                                         loop_stop=data["end"],
                                         zoom_start=data["start"],
                                         zoom_stop=data["end"],
                                         fps=data["fps"])

    if data.get("new"):
        logger.details.set_header(u"新規ファイルで開始しました:")
        return {"return_code": return_code}

    else:
        logger.details.set_header(u"ファイルを開きました:")
        logger.details.add_detail("file name:\n{}".format(file_path))
        return {"return_code": return_code, "update_context": update_context}

if __name__ == "__builtin__":
    piece_data = {}
    data = {"path": "E:/works/client/keica/data/assets/Mia.v1.1.fbx"}

    main({"data": data})
