#-*- coding: utf8 -*-

import os
import sys

from pyfbsdk import *


mod = "{}/source/python".format(os.environ["KEICA_TOOL_PATH"])
if not mod in sys.path:
    sys.path.append(mod)
print mod
from puzzle.Piece import Piece
import KcLibs.mobu.kc_model as kc_model

from KcLibs.mobu.KcRender import *

_PIECE_NAME_ = "RenderScene"

class RenderScene(Piece):
    def __init__(self, **args):
        """
        description:
            open_path - open path
        """
        super(RenderScene, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self):
        flg = True
        header = ""
        detail = ""

        render = KcRender()

        cam = False
        for camera in FBSystem().Scene.Cameras:
            long_name = camera.LongName
            if not ":" in long_name:
                continue

            namespace = long_name.split(":")[0]

            if "cam_{}".format(self.data["shot_name"]) ==  namespace:
                cam = camera
                break

        if not cam:
            self.logger.debug("cam is not exists: {}".format("cam_{}".format(self.data["shot_name"])))
            flg = False
            header = u"render シーンにカメラがありませんでした: {}".format(namespace)
            detail = ""
            return flg, self.pass_data, header, detail    

        if self.data["fps"] != 24:
            pass

        render.start = self.data["start"]
        render.end = self.data["end"]
        render.fps = self.data["fps"]
        if self.data["render_scale"] != 1:
          render.render_scale = self.data["render_scale"]

        render.execute(cam, str(self.data["movie_path"]))

        self.logger.debug("render to: {}".format(self.data["movie_path"]))
        header = u"renderしました"
        detail = u"path: \n{}\nstart: {}\nend  : {}\nfps  : {}\nscale: {}".format(self.data["movie_path"], 
                                                                                  self.data["start"],
                                                                                  self.data["end"],
                                                                                  self.data["fps"], 
                                                                                  self.data["render_scale"])

        return flg, self.pass_data, header, detail

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



    x = RenderScene(piece_data=piece_data, data=data)
    x.execute()

    print x.pass_data


    start = 4
    end = 8

    fps = 30
    print "base"
    print "start :", start
    print "end   :", end
    print "fps   :", fps

    print

    value = 24.0/fps


    print "start :", start * value
    print "end   :", end * value
    print "fps   :", fps * value


