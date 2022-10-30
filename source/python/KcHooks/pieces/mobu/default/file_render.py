#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env

from puzzle2.PzLog import PzLog

TASK_NAME = "file_render"

def main(event={}, context={}):
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    print("select camera")
    print("set size")

    return {"return_code": return_code}

if __name__ == "__builtin__":

    piece_data = {}

    data = {
           "mobu_movie_path": "",
           "width": 1920,
           "height": 1080,
           "start": 0,
           "end": 100
            }

    main({"data": data})
