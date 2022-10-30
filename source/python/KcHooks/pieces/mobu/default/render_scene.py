#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env
import KcLibs.mobu.kc_model as kc_model

from KcLibs.mobu.KcRender import *

from puzzle2.PzLog import PzLog

TASK_NAME = "render_scene"
DATA_KEY_REQUIRED = [""]

def main(event={}, context={}):
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    render = KcRender()

    cam = False
    namespace = ""
    for camera in FBSystem().Scene.Cameras:
        long_name = camera.LongName
        if not ":" in long_name:
            continue

        namespace = long_name.split(":")[0]

        if "cam_{}".format(data["shot_name"]) ==  namespace:
            cam = camera
            break

    if not cam:
        logger.debug("cam is not exists: {}".format("cam_{}".format(data["shot_name"])))
        flg = False
        header = u"render シーンにカメラがありませんでした: {}".format(namespace)
        logger.details.set_header(header)
        return {"return_code": 1}

    if data["fps"] != 24:
        pass

    render.start = data["start"]
    render.end = data["end"]
    render.fps = data["fps"]
    if data["render_scale"] != 1:
        render.render_scale = data["render_scale"]

    render.execute(cam, str(data["movie_path"]))

    logger.debug("render to: {}".format(data["movie_path"]))
    header = u"renderしました"
    detail = u"path: \n{}\nstart: {}\nend  : {}\nfps  : {}\nscale: {}".format(data["movie_path"], 
                                                                                data["start"],
                                                                                data["end"],
                                                                                data["fps"], 
                                                                                data["render_scale"])
    logger.details.set_header(header)
    logger.details.set_detail(detail)
    return {"return_code": return_code}

from KcLibs.core.KcProject import *
import KcLibs.core.kc_env as kc_env

if __name__ == "__builtin__":
    piece_data = {"include_model": True}
    
    data ={u'cut': u'005',
           'end': 0,
           'fps': 0,
           'movie_path': u'E:/works/client/keica/_942_ZIZ/3D/s01/c005/edit/mov_edit/ZIM_s01c005_anim_t01_02_amek.mov',
           'path': u'E:/works/client/keica/_942_ZIZ/3D/s01/c005/edit/ZIM_s01c005_anim_t01_02_amek_ANIM.fbx',
           u'progress': u'ANIM',
           u'project': u'ZIM',
           u'project_variation': u'home',
           u'scene': u'01',
           'shot_name': 's01c005',
           'start': 0,
           u'take': u'01',
           'user': 'amek',
           "render_fps": 24,
           u'version': u'02'}

    main({"data": data})

    start = 4
    end = 8

    fps = 30
    print("base")
    print("start :", start)
    print("end   :", end)
    print("fps   :", fps)

    print

    value = 24.0/fps


    print("start :", start * value)
    print("end   :", end * value)
    print("fps   :", fps * value)


