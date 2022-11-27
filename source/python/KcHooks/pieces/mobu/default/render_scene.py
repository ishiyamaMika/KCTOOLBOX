#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *

sys_path = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
sys_path = os.path.normpath(sys_path).replace("\\", "/")
if sys_path not in sys.path: 
    sys.path.append(sys_path)

import KcLibs.core.kc_env as kc_env

from KcLibs.mobu.KcRender import KcRender

from puzzle2.PzLog import PzLog

TASK_NAME = "render_scene"

def main(event={}, context={}):
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0
    render = KcRender()

    cam = False
    namespace = ""

    if data.get("render_type") == "switcher":
        cam = "switcher"

    else:
        for camera in FBSystem().Scene.Cameras:
            long_name = camera.LongName
            # if ":" not in long_name:
            #     continue
            if "camera_name" in data:
                if data["camera_name"] in long_name:
                    cam = camera
                    break
            else:
                namespace = long_name.split(":")[0]

                if "cam_{}".format(data["shot_name"]) == namespace:
                    cam = camera
                    break

    if not cam:
        if "camera_name" in data:
            logger.debug("cam is not exists: {}".format("cam_{}".format(data["camera_name"])))
            header = u"render シーンにカメラがありませんでした: {}".format(data["camera_name"])
        else:
            logger.debug("cam is not exists: {}".format("cam_{}".format(data["shot_name"])))
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
    movie_path = str(data["movie_path"])
    if "rename_movie_file" in data:
        for k, v in data["rename_movie_file"].items():
            logger.debug("rename_movie_file: {} -> {}".format(k, v))
            logger.details.add_detail("rename_movie_file: {} -> {}".format(k, v))
            movie_path = movie_path.replace(k, v)
    
    if "add_suffix" in data:
        d, f = os.path.split(movie_path)
        f, ext = os.path.splitext(f)
        movie_path = "{}/{}{}{}".format(d, f, data["add_suffix"], ext)

    result = render.execute(cam, movie_path)
    logger.debug(result)
    logger.debug("render to: {}".format(movie_path))
    logger.details.add_detail("render to: {}".format(movie_path))

    header = u"renderしました: {}".format(os.path.basename(movie_path))
    detail = u"path: \n{}\nstart: {}\nend  : {}\nfps  : {}\nscale: {}".format(data["movie_path"],
                                                                              data["start"],
                                                                              data["end"],
                                                                              data["fps"],
                                                                              data["render_scale"])
    logger.details.set_header(header)
    logger.details.add_detail(detail)
    return {"return_code": return_code}


if __name__ in ["__builtin__", "builtins"]:
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


