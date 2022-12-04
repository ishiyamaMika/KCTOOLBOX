from inspect import trace
import os
import sys
import json


sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env
from KcLibs.core.KcProject import KcProject

from puzzle2.PzLog import PzLog

TASK_NAME = "create_directories"


def main(event={}, context={}):
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    header = "create directories"
    detail = ""
    path = data["path"]
    cut_root = os.path.normpath(os.path.join(path, "../../../"))
    directories = ["_OUTPUT",
                    "aep",
                    "aep/_Sozai",
                    "aep/render",
                    "3D",
                    "3D/edit",
                    "3D/rend"
                    ]
    
    for group in data["groups"]:
        directories.append("aep/render/{}".format(group))

    for each in directories:
        directory = "{}/{}".format(cut_root, each)
        if not os.path.lexists(directory):
            try:
                os.makedirs(directory)
                detail += u"create successed: {}\n".format(directory)
                if logger:
                    logger.debug(u"create successed: {}".format(directory))
            except:
                detail += u"create failed   : {}\n".format(directory)
                if logger:
                    logger.debug(u"create failed   : {}".format(directory))

    logger.details.set_header(return_code, header)
    logger.details.add_detail(detail)

    return {"return_code": return_code}


if __name__ in ["__main__", "__builtin__"]:
    data = {
            "shot_name": "s99c500",
            "end": 40,
            "render_scale": 0.5,
            "start": 0,
            "camera": "cam_s99c500:Merge_Camera",
            "movie_path": "X:/Project/_942_ZIZ/3D/s99/c500/movie_convert/max/ZIM_s99c500_max.avi",
            "fps": 8,
            "path": "X:/Project/_942_ZIZ/2020_ikimono_movie/_work/14_partC_Japan/26_animation/s99/c500/3D/master/ZIM_s99c500_anim.max"
        }
    
    main({"data": data})
