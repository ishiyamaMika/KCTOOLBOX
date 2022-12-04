#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env

import KcLibs.mobu.kc_transport_time as kc_transport_time

from puzzle2.PzLog import PzLog

TASK_NAME = "change_time"

def main(event={}, context={}):
    """
    puece_data: mode, fps
    pass_data: @start, @end, @fps, TASK_NAME
    """
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger
    logger.details.get_all()
    return_code = 0
    update_context = {}

    header = str(data)
    detail = ""
    if "revert_times" in data:
        header = "revert scene time"
        detail = "revert time to: {loop_start} {zoom_start}-{zoom_stop} {loop_stop}({fps})".format(**data["revert_times"])

        header = u"シーンのフレームを戻しました"
        kc_transport_time.set_scene_time(**data["revert_times"])
        logger.debug(detail)

    else:
        scene_time = kc_transport_time.get_scene_time()
        update_context["{}.scene_times".format(TASK_NAME)] = scene_time

        if scene_time["fps"] != data["fps"]:
            if data["fps"] > data["fps"]:
                value = data["fps"] / data["fps"]
                start = data["start"] * value
                end = data["end"] * value + (value-1)
            else:
                value = data["fps"] / data["fps"]
                start = data["start"] / value
                end = data["end"] / value

            fps = data["fps"]
        else:
            start = data["start"]
            end = data["end"]
            fps = data["fps"]
      
        kc_transport_time.set_scene_time(loop_start=int(start),
                                         loop_stop=int(end),
                                         zoom_start=int(start),
                                         zoom_stop=int(end),
                                         fps=fps)

        new_time = kc_transport_time.get_scene_time()

        detail = "change time to: {}-{}({}) -> {}-{}({})".format(data["start"],
                                                                 data["end"],
                                                                 data["fps"],
                                                                 new_time["loop_start"], 
                                                                 new_time["loop_stop"], 
                                                                 new_time["fps"])

        header = u"シーンのフレームを変更しました"
        logger.debug(detail)

        update_context["start"] = start
        update_context["end"] = end
        update_context["fps"] = fps

    logger.details.set_header(return_code, header)
    logger.details.add_detail(detail)

    return {"return_code": return_code, "update_context": update_context}

from KcLibs.core.KcProject import *
import KcLibs.core.kc_env as kc_env

if __name__ == "builtins":
    piece_data = {"fps": 24}
    
    data ={u'cut': u'005',
           'start': 0,
           'end': 20,
           'fps': 8,
           'movie_path': u'E:/works/client/keica/_942_ZIZ/3D/s01/c005/edit/mov_edit/ZIM_s01c005_anim_t01_02_amek.fbx',
           'path': u'E:/works/client/keica/_942_ZIZ/3D/s01/c005/edit/ZIM_s01c005_anim_t01_02_amek_ANIM.fbx',
           u'progress': u'ANIM',
           u'project': u'ZIM',
           u'project_variation': u'home',
           u'scene': u'01',
           'shot_name': 's01c005',
           u'take': u'01',
           'user': 'amek',
           "render_fps": 24,
           u'version': u'02'}

    pass_data = {"revert_times": {
                            "loop_start": 10,
                            "loop_stop": 200,
                            "zoom_start": 10,
                            "zoom_stop": 100,
                            "fps": 24
                            }
                     }

    # data.update(pass_data)

    main({"data": data})
